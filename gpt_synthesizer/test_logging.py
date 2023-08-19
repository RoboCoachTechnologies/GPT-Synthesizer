import sys
import logging

# Configure the logging format

# Open the file in write mode
with open('terminal_log.log', 'w') as file:
    pass  # This will effectively erase the contents of the file

logging.basicConfig(
    filename='terminal_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define a custom stream handler to capture console output
class ConsoleAndFileHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)
    
    def emit(self, record):
        super().emit(record)
        self.stream.flush()  # Flush the stream to capture the output immediately

# Create an instance of the custom handler
console_handler = ConsoleAndFileHandler(sys.stdout)

# Add the custom handler to the logger
logger = logging.getLogger()
logger.propagate = False
logger.addHandler(console_handler)
# logger.propagate = False

# Log any input and output from the terminal
while True:
    logging.info(f'Enter something:')
    # user_input = input()
    # logging.info(user_input)
   
# Close the logging file handler
logging.shutdown()
