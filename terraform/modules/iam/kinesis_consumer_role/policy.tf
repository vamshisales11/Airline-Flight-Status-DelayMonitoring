resource "aws_iam_role_policy" "kinesis_read_policy" {
  name = "airline-delay-monitoring-${var.environment}-kinesis-read-policy"
  role = aws_iam_role.kinesis_consumer.id

  policy = data.aws_iam_policy_document.kinesis_read_access.json
}

data "aws_iam_policy_document" "kinesis_read_access" {
  statement {
    actions = [
      "kinesis:DescribeStream",
      "kinesis:GetRecords",
      "kinesis:GetShardIterator",
      "kinesis:ListStreams",
      "kinesis:ListShards"
    ]
    resources = ["*"] # Optionally restrict to your stream ARN for tighter security
  }
}
