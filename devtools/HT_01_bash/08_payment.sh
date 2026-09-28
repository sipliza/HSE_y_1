cd payment-service
cat > config/payment.conf <<EOF
SERVICE_NAME=payment-service
SERVICE_VERSION=1.0
CURRENCY=EUR
PAYMENT_PROVIDER=TEST
MAX_PAYMENT=5000
LOG_LEVEL=INFO
EOF
cp config/payment.conf backup/payment.conf.bak