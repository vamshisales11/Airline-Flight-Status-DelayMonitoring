terraform {
  backend "s3" {
    bucket = "airline-monitoring-terraform-state-dev"
    key    = "global/s3/terraform.tfstate"
    region = "us-east-1"
    profile = "vamshi2"
    encrypt = true
    # dynamodb_table is not needed—for personal project becasue statelock is not requiremed
  }
}
