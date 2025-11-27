module "s3" {
  source      = "./modules/s3"
  environment = var.environment
}
module "kinesis_stream" {
  source      = "./modules/kinesis"
  environment = var.environment
}

module "kinesis_consumer_role" {
  source      = "./modules/iam/kinesis_consumer_role"
  environment = var.environment
}

module "s3_access_role" {
  source             = "./modules/iam/s3_access_role"
  environment        = var.environment
  raw_bucket_arn     = module.s3.raw_bucket_arn   # Output from your S3 module
  processed_bucket_arn = module.s3.processed_bucket_arn
}


module "redshift_serverless" {
  source = "./modules/redshift_serverless"

  environment         = var.environment
  admin_username      = var.redshift_serverless_username
  admin_user_password = var.redshift_serverless_password
  redshift_role_arn   = module.iam_redshift_serverless_s3_role.role_arn
}



module "iam_redshift_serverless_s3_role" {
  source = "./modules/iam/redshift_serverless_s3_role"

  environment          = var.environment
  raw_bucket_arn       = module.s3.raw_bucket_arn
  processed_bucket_arn = module.s3.processed_bucket_arn
}


module "glue_service_role" {
  source               = "./modules/iam/glue_service_role"
  environment          = var.environment
  raw_bucket_arn       = module.s3.raw_bucket_arn
  processed_bucket_arn = module.s3.processed_bucket_arn
}


module "glue_catalog" {
  source      = "./modules/glue"
  environment = var.environment

  raw_bucket_name       = module.s3.raw_bucket_name
  processed_bucket_name = module.s3.processed_bucket_name
  glue_role_arn         = module.glue_service_role.glue_role_arn
}
