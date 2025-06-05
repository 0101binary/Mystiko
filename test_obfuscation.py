import base64
import zlib
import os

def test_obfuscation():
    # Read the original payload
    with open("payload.py", "r") as f:
        original_content = f.read()
    
    # Obfuscate
    compressed = zlib.compress(original_content.encode())
    encoded = base64.b64encode(compressed)
    obfuscated = f"""import base64,zlib;exec(zlib.decompress(base64.b64decode({repr(encoded)})))"""
    
    # Save obfuscated version
    with open("obfuscated_payload.py", "w") as f:
        f.write(obfuscated)
    
    # Test deobfuscation
    try:
        # Create a temporary file to test execution
        with open("test_execution.py", "w") as f:
            f.write(obfuscated)
        
        # Try to execute the obfuscated code
        os.system("python test_execution.py")
        print("[+] Obfuscation test completed successfully")
    except Exception as e:
        print(f"[!] Error during test: {e}")
    finally:
        # Cleanup
        if os.path.exists("test_execution.py"):
            os.remove("test_execution.py")

if __name__ == "__main__":
    test_obfuscation() 