output "role_arn" {
  description = "IAM role ARN for Redshift Serverless COPY/UNLOAD"
  value       = aws_iam_role.redshift_serverless_s3.arn
}
