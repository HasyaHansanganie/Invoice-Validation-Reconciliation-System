from zeep import Client

def validate_amount_with_soap(amount: float) -> str:
    
    """
    Simulate a validation step by converting a number (invoice amount)
    into its word representation using a public SOAP API.
    Args:
        amount (float): The invoice amount to be validated.
    Returns:
        str: Validation status message (e.g., 'Valid: One Thousand').
             Returns 'Validation failed' if an error occurs.
    """
    try:
        # Initialize SOAP client with NumberConversion WSDL
        client = Client("http://www.dataaccess.com/webservicesserver/NumberConversion.wso?WSDL")

        # Call the NumberToWords service with the invoice amount (as integer)
        word_result = client.service.NumberToWords(int(amount))

        # Return a "Valid" status with the amount in words
        return f"Valid: {word_result.strip()}"

    except Exception as e:
        print(f"SOAP error: {e}")
        return "Validation failed"
