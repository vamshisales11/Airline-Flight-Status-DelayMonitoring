resource "aws_redshiftserverless_namespace" "airline" {
  namespace_name      = "airline-${var.environment}-ns"
  admin_username      = var.admin_username
  admin_user_password = var.admin_user_password

  default_iam_role_arn = var.redshift_role_arn
  iam_roles = [
    var.redshift_role_arn
  ]

  tags = {
    Project     = "airline-flight-status-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}


resource "aws_redshiftserverless_workgroup" "airline" {
  workgroup_name = "airline-${var.environment}-wg"
  namespace_name = aws_redshiftserverless_namespace.airline.namespace_name
  base_capacity  = var.base_capacity

  tags = {
    Project     = "airline-flight-status-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
