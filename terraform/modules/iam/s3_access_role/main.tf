resource "aws_iam_role" "s3_access" {
  name = "airline-delay-monitoring-${var.environment}-s3-access-role"
  assume_role_policy = data.aws_iam_policy_document.s3_assume_role.json

  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

data "aws_iam_policy_document" "s3_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"] # Change to "lambda.amazonaws.com" if using Lambda
    }
  }
}
