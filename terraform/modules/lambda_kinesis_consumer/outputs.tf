output "lambda_function_arn" {
  value       = aws_lambda_function.kinesis_consumer.arn
  description = "ARN of the Kinesis consumer Lambda"
}

output "lambda_role_arn" {
  value       = aws_iam_role.lambda_kinesis_consumer.arn
  description = "ARN of the Lambda execution role"
}
