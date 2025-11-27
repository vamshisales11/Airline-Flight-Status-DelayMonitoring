resource "aws_iam_role_policy" "s3_rw_policy" {
  name   = "airline-delay-monitoring-${var.environment}-s3-rw-policy"
  role   = aws_iam_role.s3_access.id
  policy = data.aws_iam_policy_document.s3_rw_access.json
}

data "aws_iam_policy_document" "s3_rw_access" {
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = [
      "${var.raw_bucket_arn}",
      "${var.raw_bucket_arn}/*",
      "${var.processed_bucket_arn}",
      "${var.processed_bucket_arn}/*"
    ]
  }
}
