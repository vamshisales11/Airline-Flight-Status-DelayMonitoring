variable "lambda_function_name" {
  type        = string
  description = "Name of the Lambda function that consumes Kinesis events"
}

variable "kinesis_stream_arn" {
  type        = string
  description = "ARN of the Kinesis Data Stream to consume from"
}

variable "lambda_zip_path" {
  type        = string
  description = "Local path to the Lambda deployment package (zip file)"
}


variable "alerts_topic_arn" {
  type        = string
  description = "SNS topic ARN for alerts"
}

variable "alerts_queue_arn" {
  type        = string
  description = "SQS queue ARN for alerts"
}


variable "alerts_queue_url" {
  type        = string
  description = "SQS queue URL for alerts"
}


