output "alerts_topic_arn" {
  value       = aws_sns_topic.flight_delay_alerts.arn
  description = "SNS topic ARN for flight delay alerts"
}

output "alerts_queue_url" {
  value       = aws_sqs_queue.flight_delay_alerts_queue.id
  description = "SQS queue URL for flight delay alerts"
}

output "alerts_queue_arn" {
  value       = aws_sqs_queue.flight_delay_alerts_queue.arn
  description = "SQS queue ARN for flight delay alerts"
}
