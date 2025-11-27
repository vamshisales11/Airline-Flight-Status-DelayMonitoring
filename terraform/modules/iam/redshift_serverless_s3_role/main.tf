data "aws_iam_policy_document" "assume_by_redshift" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["redshift.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "s3_copy_unload" {
  statement {
    sid    = "AllowReadFromRawAndProcessed"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      var.raw_bucket_arn,
      "${var.raw_bucket_arn}/*",
      var.processed_bucket_arn,
      "${var.processed_bucket_arn}/*",
    ]
  }

  statement {
    sid    = "AllowUnloadToProcessed"
    effect = "Allow"

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "${var.processed_bucket_arn}/*",
    ]
  }
}

resource "aws_iam_role" "redshift_serverless_s3" {
  name               = "airline-${var.environment}-redshift-serverless-s3-role"
  assume_role_policy = data.aws_iam_policy_document.assume_by_redshift.json

  description = "IAM role for Redshift Serverless to COPY/UNLOAD with S3"

  tags = {
    Project     = "airline-flight-status-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_iam_role_policy" "redshift_serverless_s3" {
  name   = "airline-${var.environment}-redshift-serverless-s3-policy"
  role   = aws_iam_role.redshift_serverless_s3.id
  policy = data.aws_iam_policy_document.s3_copy_unload.json
}
