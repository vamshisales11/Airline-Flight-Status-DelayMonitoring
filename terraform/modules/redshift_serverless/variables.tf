variable "environment" {
  description = "Deployment environment (dev, prod, etc.)"
  type        = string
}

variable "admin_username" {
  description = "Admin username for Redshift Serverless"
  type        = string
}

variable "admin_user_password" {
  description = "Admin password for Redshift Serverless"
  type        = string
  sensitive   = true
}

variable "base_capacity" {
  description = "Base RPUs for Redshift Serverless workgroup"
  type        = number
  default     = 8
}



variable "redshift_role_arn" {
  description = "IAM role ARN for Redshift Serverless COPY/UNLOAD"
  type        = string
}

