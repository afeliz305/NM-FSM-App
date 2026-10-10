# ecs.tf
# ECR repository created by staging only, shared across workspaces
# Production references the same repo via data source below
resource "aws_ecr_repository" "flask_app" {
  count                = terraform.workspace == "staging" ? 1 : 0
  name                 = "nm-fsm-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  tags                 = { Name = "nm-fsm-app" }
}

# ECR data source used by production to reference the shared repo
data "aws_ecr_repository" "flask_app" {
  count = terraform.workspace == "production" ? 1 : 0
  name  = "nm-fsm-app"
}

# Local to unify ECR URL regardless of workspace
locals {
  ecr_repository_url = terraform.workspace == "staging" ? aws_ecr_repository.flask_app[0].repository_url : data.aws_ecr_repository.flask_app[0].repository_url
}

# ECS cluster shared, one per account
resource "aws_ecs_cluster" "main" {
  name = "cis4641-cluster"
  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

# ECS Fargate service workspace-specific
resource "aws_ecs_service" "app" {
  name            = "flask-${terraform.workspace}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = [data.aws_subnet.public.id]
    security_groups  = [aws_security_group.fargate.id]
    assign_public_ip = true
  }
  lifecycle {
    ignore_changes = [desired_count]
  }
}

# ECS task definition workspace-specific
resource "aws_ecs_task_definition" "app" {
  family                   = "flask-${terraform.workspace}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = data.aws_iam_role.lab.arn
  container_definitions = jsonencode([{
    name         = "flask-app"
    image        = "${local.ecr_repository_url}:${var.flask_image_tag}"
    portMappings = [{ containerPort = 5000, protocol = "tcp" }]
    environment = [
      {
        name  = "DATABASE_URL"
        value = "mysql+pymysql://${var.db_user}:${var.db_password}@${var.db_ip[terraform.workspace]}/${var.db_name}"
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/flask-${terraform.workspace}"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# CloudWatch log group workspace-specific
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/flask-${terraform.workspace}"
  retention_in_days = 7
}

# ecs.tf — auto-scale (cost control)
data "archive_file" "scale_lambda" {
  type        = "zip"
  output_path = "${path.module}/scale_lambda-${terraform.workspace}.zip"
  source {
    filename = "index.py"
    content  = <<-PY
      import boto3
      ecs = boto3.client('ecs')
      def handler(event, context):
          count = 0 if event['detail']['state'] == 'stopped' else 1
          ecs.update_service(cluster='${aws_ecs_cluster.main.name}',
              service='flask-${terraform.workspace}',
              desiredCount=count)
    PY
  }
}

resource "aws_lambda_function" "ecs_follow_db" {
  function_name    = "ecs-follow-db-${terraform.workspace}"
  role             = data.aws_iam_role.lab.arn # LabRole
  runtime          = "python3.12"
  handler          = "index.handler"
  filename         = data.archive_file.scale_lambda.output_path
  source_code_hash = data.archive_file.scale_lambda.output_base64sha256
}

# Fire on THIS workspace's MySQL instance state changes
resource "aws_cloudwatch_event_rule" "mysql_state" {
  name = "mysql-state-${terraform.workspace}"
  event_pattern = jsonencode({
    source        = ["aws.ec2"]
    "detail-type" = ["EC2 Instance State-change Notification"]
    detail = {
      state         = ["stopped", "running"]
      "instance-id" = [aws_instance.mysql_db.id]
    }
  })
}

resource "aws_cloudwatch_event_target" "scale" {
  rule = aws_cloudwatch_event_rule.mysql_state.name
  arn  = aws_lambda_function.ecs_follow_db.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ecs_follow_db.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.mysql_state.arn
}
