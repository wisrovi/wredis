Frequently Asked Questions
================================================================================

General Questions
--------------------------------------------------------------------------------

**What is the minimum Python version supported?**
WRedis requires Python 3.10 or higher. This ensures we can use the latest type hinting and asyncio features.

**Is WRedis thread-safe?**
Yes, sychronous managers use connection pooling which is thread-safe. For asynchronous applications, use the ``Async`` variants.

Troubleshooting
--------------------------------------------------------------------------------

**Why am I getting a ConnectionError?**
Check if your Redis server is running and reachable from your application. Verify the host and port settings.

**The cache decorator is not working!**
Ensure you have the ``redis`` package installed and the server is accessible. Also, check that your function arguments are JSON-serializable, as WRedis uses them to generate cache keys.
