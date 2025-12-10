#!/bin/bash
# Provision EC2 instance for gs-convert Web UI
# Requires: AWS CLI installed and configured

set -e

echo "🚀 Provisioning EC2 instance for gs-convert..."

# Configuration
INSTANCE_NAME="gs-convert-web"
INSTANCE_TYPE="t4g.micro"
KEY_NAME="gs-convert-key"
SECURITY_GROUP_NAME="gs-convert-web-sg"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

# Find latest Ubuntu 22.04 ARM64 AMI
echo "📦 Finding latest Ubuntu 22.04 ARM64 AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*" \
              "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text \
    --region "$REGION")

if [ -z "$AMI_ID" ]; then
    echo "❌ Could not find Ubuntu 22.04 ARM64 AMI"
    exit 1
fi

echo "✅ Found AMI: $AMI_ID"

# Check if key pair exists
echo "🔑 Checking for key pair..."
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "📝 Creating key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --query 'KeyMaterial' \
        --output text \
        --region "$REGION" > "${KEY_NAME}.pem"

    chmod 400 "${KEY_NAME}.pem"
    echo "✅ Key pair saved to ${KEY_NAME}.pem"
else
    echo "✅ Key pair already exists: $KEY_NAME"
fi

# Check if security group exists
echo "🔒 Checking for security group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region "$REGION" 2>/dev/null)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    echo "📝 Creating security group: $SECURITY_GROUP_NAME"

    # Get default VPC ID
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=isDefault,Values=true" \
        --query 'Vpcs[0].VpcId' \
        --output text \
        --region "$REGION")

    # Create security group
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for gs-convert web UI" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId' \
        --output text \
        --region "$REGION")

    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"

    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"

    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"

    echo "✅ Security group created: $SG_ID"
else
    echo "✅ Security group already exists: $SG_ID"
fi

# Launch instance
echo "🖥️  Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=20,VolumeType=gp3,DeleteOnTermination=true}' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text \
    --region "$REGION")

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance to be running
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running \
    --instance-ids "$INSTANCE_ID" \
    --region "$REGION"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region "$REGION")

echo "✅ Instance is running"
echo "📍 Public IP: $PUBLIC_IP"

# Allocate and associate Elastic IP
echo "🌐 Allocating Elastic IP..."
ALLOCATION_ID=$(aws ec2 allocate-address \
    --domain vpc \
    --query 'AllocationId' \
    --output text \
    --region "$REGION")

echo "✅ Elastic IP allocated: $ALLOCATION_ID"

# Associate Elastic IP with instance
aws ec2 associate-address \
    --instance-id "$INSTANCE_ID" \
    --allocation-id "$ALLOCATION_ID" \
    --region "$REGION" >/dev/null

# Get Elastic IP
ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids "$ALLOCATION_ID" \
    --query 'Addresses[0].PublicIp' \
    --output text \
    --region "$REGION")

echo "✅ Elastic IP associated: $ELASTIC_IP"

# Wait a bit for SSH to be ready
echo "⏳ Waiting 30 seconds for SSH to be ready..."
sleep 30

# Output summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ EC2 INSTANCE PROVISIONED SUCCESSFULLY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Instance ID:       $INSTANCE_ID"
echo "Instance Type:     $INSTANCE_TYPE"
echo "Elastic IP:        $ELASTIC_IP"
echo "Security Group:    $SG_ID"
echo "Key Pair:          $KEY_NAME"
echo "Region:            $REGION"
echo ""
echo "Next steps:"
echo "  1. SSH into instance:"
echo "     ssh -i ${KEY_NAME}.pem ubuntu@${ELASTIC_IP}"
echo ""
echo "  2. Run deployment script:"
echo "     ./scripts/deploy-app.sh ${ELASTIC_IP} ${KEY_NAME}.pem"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Save instance info to file
cat > .aws-instance-info << EOF
INSTANCE_ID=$INSTANCE_ID
ELASTIC_IP=$ELASTIC_IP
SECURITY_GROUP_ID=$SG_ID
KEY_NAME=$KEY_NAME
REGION=$REGION
EOF

echo ""
echo "Instance info saved to .aws-instance-info"
