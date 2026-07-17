# AWS Elastic Beanstalk Deployment Guide

Since I do not have direct access to your AWS credentials or AWS Console, you will need to perform the upload yourself. This guide shows you the two easiest methods to launch your Dynamic Pricing Engine online.

---

## Method 1: The AWS Web Console (Easiest & Recommended)

This method uses the graphical interface of the AWS Console.

### Step 1: Package Your Code into a ZIP File
You must zip your project files, but **exclude the `.venv` and `.git` folders** (since they contain thousands of local files and will make the zip too large to upload).

To do this automatically in Windows PowerShell:
1. Open PowerShell in your project directory (`c:\Java_DSA\DynamicPrice_project`).
2. Run this command to create a clean zip file containing only the required deployment files:
   ```powershell
   Compress-Archive -Path "application.py", "requirements.txt", "Procfile", ".ebextensions", "model.joblib", "q_table.csv" -DestinationPath "dynamic-pricing-deployment.zip" -Force
   ```
   *This creates a small file called `dynamic-pricing-deployment.zip` in your root folder.*

### Step 2: Upload to AWS Elastic Beanstalk
1. Log in to the [AWS Management Console](https://aws.amazon.com/console/).
2. In the search bar at the top, search for **Elastic Beanstalk** and click it.
3. Click the **Create Application** (or **Create Environment**) button.
4. Fill in the configuration fields:
   - **Application Name**: `Dynamic-Pricing-Engine`
   - **Platform**: Select **Python** from the dropdown menu.
   - **Platform Branch**: Select **Python 3.10 running on 64bit Amazon Linux 2023** (or the version matching your local environment).
   - **Platform Version**: Leave as the default recommended version.
5. In the **Application Code** section:
   - Select **Upload your code**.
   - For **Source code origin**, select **Local file**.
   - Click **Choose file** and select the `dynamic-pricing-deployment.zip` you created in Step 1.
6. Click **Next** or **Create application**.
7. AWS will now spin up a virtual machine (EC2 instance), install all packages from your `requirements.txt` file, launch Gunicorn using the `Procfile`, and give you a public URL (e.g., `http://dynamic-pricing-engine.env.ebd.amazonaws.com`).

---

## Method 2: Deploying via the EB CLI (Advanced)

If you prefer using the command line to deploy and update the code directly:

### Step 1: Install the AWS Elastic Beanstalk CLI
Activate your virtual environment and install the CLI tool:
```bash
pip install awsebcli
```

### Step 2: Initialize Your Beanstalk Project
Run the initialization wizard:
```bash
eb init -p python-3.10 dynamic-pricing-engine
```
*It will ask you to select a region and prompt you to input your AWS Access Key and Secret Key (which you can generate in your AWS IAM Console).*

### Step 3: Create and Launch the Environment
Deploy the app to a new live environment:
```bash
eb create pricing-env
```
*This command will bundle your code, upload it to AWS, configure the servers, and open up a live endpoint automatically.*

### Step 4: Deploying Code Updates
If you change your model or code later and want to push the updates live, simply run:
```bash
eb deploy
```
