resource "aws_sns_topic" "flight_delay_alerts" {
  name = "airline-dev-flight-delay-alerts"
}

resource "aws_sqs_queue" "flight_delay_alerts_queue" {
  name = "airline-dev-flight-delay-alerts-queue"
}
