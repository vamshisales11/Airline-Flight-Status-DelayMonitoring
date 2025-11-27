resource "aws_iam_role" "kinesis_consumer" {
  name = "airline-delay-monitoring-${var.environment}-kinesis-consumer-role"
  assume_role_policy = data.aws_iam_policy_document.kinesis_assume_role.json

  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

data "aws_iam_policy_document" "kinesis_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"] # or ec2.amazonaws.com, glue.amazonaws.com etc.
    }
  }
}
