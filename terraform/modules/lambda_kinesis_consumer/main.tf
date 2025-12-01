########################################
# IAM Role for Lambda Kinesis Consumer
########################################

resource "aws_iam_role" "lambda_kinesis_consumer" {
  name = "${var.lambda_function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Basic CloudWatch Logs permissions
resource "aws_iam_role_policy" "lambda_basic_logging" {
  name = "${var.lambda_function_name}-logging"
  role = aws_iam_role.lambda_kinesis_consumer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

########################################
# Lambda Function
########################################

resource "aws_lambda_function" "kinesis_consumer" {
  function_name = var.lambda_function_name

  role    = aws_iam_role.lambda_kinesis_consumer.arn
  runtime = "python3.10"
  handler = "lambda_kinesis_consumer.lambda_handler"

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  timeout = 60

  environment {
    variables = {
      ALERTS_TOPIC_ARN = var.alerts_topic_arn
      ALERTS_QUEUE_URL = var.alerts_queue_url
    }
  }
}

########################################
# Kinesis → Lambda Event Source Mapping
########################################

resource "aws_lambda_event_source_mapping" "kinesis_to_lambda" {
  event_source_arn  = var.kinesis_stream_arn
  function_name     = aws_lambda_function.kinesis_consumer.arn
  starting_position = "LATEST"   # only process new records
  batch_size        = 100
  enabled           = true
}



# Allow Lambda to read from the Kinesis stream
resource "aws_iam_role_policy" "lambda_kinesis_read" {
  name = "${var.lambda_function_name}-kinesis-read"
  role = aws_iam_role.lambda_kinesis_consumer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:DescribeStream",
          "kinesis:DescribeStreamSummary",
          "kinesis:ListShards",
          "kinesis:ListStreams"
        ]
        Resource = var.kinesis_stream_arn
      }
    ]
  })
}



# Allow Lambda to write bad events to S3 quarantine
resource "aws_iam_role_policy" "lambda_s3_quarantine_write" {
  name = "${var.lambda_function_name}-s3-quarantine-write"
  role = aws_iam_role.lambda_kinesis_consumer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::airline-delay-monitoring-dev-processed-data",
          "arn:aws:s3:::airline-delay-monitoring-dev-processed-data/*"
        ]
      }
    ]
  })
}




# Allow Lambda to publish alerts to SNS
resource "aws_iam_role_policy" "lambda_sns_publish" {
  name = "${var.lambda_function_name}-sns-publish"
  role = aws_iam_role.lambda_kinesis_consumer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = var.alerts_topic_arn
      }
    ]
  })
}

# Allow Lambda to send alert messages to SQS
resource "aws_iam_role_policy" "lambda_sqs_send" {
  name = "${var.lambda_function_name}-sqs-send"
  role = aws_iam_role.lambda_kinesis_consumer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = var.alerts_queue_arn
      }
    ]
  })
}
