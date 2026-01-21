"""
Comprehensive email debugging script.
Checks all mail documents for delivery status and errors.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 60)
print("EMAIL DELIVERY DEBUG REPORT")
print("=" * 60)
print()

# Get ALL mail documents
mail_docs = list(db.collection("mail").get())

if not mail_docs:
    print("❌ NO DOCUMENTS found in 'mail' collection!")
    print()
    print("Possible issues:")
    print("  1. The collection name in extension config doesn't match 'mail'")
    print("  2. Documents are being written to a different collection")
    exit(1)

print(f"Found {len(mail_docs)} document(s) in 'mail' collection:\n")

for doc in mail_docs:
    data = doc.to_dict()
    print(f"📧 Document: {doc.id}")
    print(f"   To: {data.get('to', 'N/A')}")
    print(f"   Subject: {data.get('message', {}).get('subject', 'N/A')[:50]}")
    
    delivery = data.get('delivery')
    
    if delivery:
        state = delivery.get('state', 'UNKNOWN')
        print(f"   State: {state}")
        
        if state == 'ERROR':
            error = delivery.get('error', 'No error details')
            print(f"   ❌ ERROR: {error}")
            
            # Parse error info
            info = delivery.get('info', {})
            if info:
                response = info.get('response', '')
                print(f"   Response: {response}")
                
        elif state == 'SUCCESS':
            info = delivery.get('info', {})
            print(f"   ✅ Delivered at: {delivery.get('endTime', 'N/A')}")
            print(f"   Message ID: {info.get('messageId', 'N/A')}")
            
        elif state == 'PENDING':
            print(f"   ⏳ Still pending...")
            attempts = delivery.get('attempts', 0)
            print(f"   Attempts: {attempts}")
            
        elif state == 'RETRY':
            print(f"   🔄 Retrying...")
            
        # Show start/end times if available
        start_time = delivery.get('startTime')
        end_time = delivery.get('endTime')
        if start_time:
            print(f"   Started: {start_time}")
        if end_time:
            print(f"   Ended: {end_time}")
    else:
        print(f"   ⚠️  NO 'delivery' field found!")
        print(f"   This means the extension has NOT processed this document.")
        print(f"   Raw data keys: {list(data.keys())}")
    
    print()

print("=" * 60)
print("DIAGNOSIS")
print("=" * 60)

# Check for common issues
has_delivery = any(doc.to_dict().get('delivery') for doc in mail_docs)
has_errors = any(doc.to_dict().get('delivery', {}).get('state') == 'ERROR' for doc in mail_docs)
has_success = any(doc.to_dict().get('delivery', {}).get('state') == 'SUCCESS' for doc in mail_docs)

if not has_delivery:
    print("""
❌ ISSUE: Extension is NOT processing documents

Possible causes:
1. Extension is not properly installed/deployed
2. Collection name mismatch (extension watching different collection)
3. Extension Cloud Function is disabled or errored

To fix:
- Go to Firebase Console → Extensions → Trigger Email
- Click 'Manage' and check the configuration
- Verify 'Email documents collection' is set to: mail
- Check Cloud Functions logs for errors
""")
elif has_errors:
    print("""
❌ ISSUE: Extension is processing but encountering ERRORS

Check the error messages above. Common causes:
1. Invalid SMTP credentials
2. SMTP server blocking connection
3. Gmail 'Less secure app access' not enabled (if using Gmail)
4. App Password required (if 2FA enabled on Gmail)

To fix Gmail SMTP:
1. Enable 2-Step Verification in Google Account
2. Create an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password in SMTP URI
""")
elif has_success:
    print("""
✅ Some emails were delivered successfully!

If you're not seeing them:
1. Check your spam/junk folder
2. Check the 'to' address is correct
3. Gmail may have filtered them
""")
else:
    print("""
⏳ Emails are PENDING

The extension may be:
1. Still processing
2. Rate limited
3. Having connectivity issues

Wait a few minutes and run this script again.
""")
