resource "aws_s3_bucket" "raw_data" {
  bucket = "airline-delay-monitoring-${var.environment}-raw-data"
  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "airline-delay-monitoring-${var.environment}-processed-data"
  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
