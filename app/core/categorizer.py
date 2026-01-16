def categorize_transaction(description):
    text = str(description).lower()
    if 'salary' in text or 'payroll' in text:
        return 'Income'
    elif 'payment' in text or 'bill' in text or 'utility' in text:
        return 'Expense'    
    elif 'transfer' in text or 'withdrawal' in text:
        return 'banking'   
    elif 'refund' in text or 'rebate' in text:
        return 'Refund'
    elif 'fee' in text or 'charge' in text:
        return 'Fee'
    elif 'interest' in text or 'dividend' in text:
        return 'Investment'
    elif 'coffee' in text or 'restaurant' in text or 'dining' in text:
        return 'Dining' 
    elif 'upi' in text or 'bank transfer' in text:
        return 'payments'
    elif 'shopping' in text or 'ecommerce' in text or 'mall' in text:
        return 'Shopping'
    elif 'client' in text or 'project' in text:
        return 'Business'
    elif 'fuel' in text or 'taxi' in text or 'transportation' in text:
        return 'Transportation'
    else:
        return 'Other'