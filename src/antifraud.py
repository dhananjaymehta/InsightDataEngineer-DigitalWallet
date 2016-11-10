"""
    Author: Dhananjay Mehta (mehta.dhananjay28@gmail.com)
    Version: v1.0

    -----------------------------------------------------------
    INSIGHT DATA ENGINEERING CODING CHALLENGE: DIGITAL WALLET
    -----------------------------------------------------------

    C H A L L A N G E   S U M M A R Y  -

    This programs has been implemented to detect fraudulent payment requests from untrusted users using digital payment
    wallet. This program has been implemented in following stages with CORE and ADDITIONAL features:

    CORE FEATURES: Features required as part of Challenge
    ----------------------------------------------------------
    STAGE 1: Batch Processing

    STAGE 2: Stream Processing: detect if a payment is TRUSTED or UNVERIFIED using three core features:

        Feature 1: Check if userA and userB have Degree 1 connectivity.
        Feature 2: Check if userA and userB have Degree 2 connectivity.
        Feature 3: Check if userA and userB have at most Degree 4 connectivity.

        "This imply that if a payment takes place between two users that are connected by at most 4th degree over
        the payment network then the payment is TRUSTED else a payment is UNVERIFIED."

    STAGE 3: Write the results of finding for each stream of payments to three separate files.

    ADDITIONAL FEATURES: AddedFeatures.py
    --------------------------------------

    RESULTS:

    Each transaction once classified will be written into three files : output1, output2, output3. These output file
    are named after features implemented to check an incoming payment.

    In addition to these output files, program will generate suspected payments report. This report will contain status
    detail of payments that were found suspicious based on new features.
"""

import sys
import csv
from collections import deque
import time
from addedfeatures import AdditionalFeatures

class AntiFraud:
    """
    AntiFraud class implements the core modules required to detect any fraudulent transaction.
    Firstly, it builds a payment social network for users in batch_payment.txt file.
    Secondly, it reads the payments from stream_payment.txt file and classify a payment as verified or unverified
    user feature1, feature2 or feature3 as required by the challenge.
    """
    def __init__(self,pay_graph=None):
        """
        initializes objects of class.
        :param pay_graph: dictionary of payments made between users; this represents the payment graph
        """
        if pay_graph is None:
            pay_graph = {}
        self.__pay_graph = pay_graph
        self.max_allowed_payment = 0
        self.status = None
        self.report = None
        self.timestamp = None
        self.user1 = None
        self.user2 = None
        self.amount = 0.0
        

        # call AddedFeatures class.
        self.added_features = AdditionalFeatures()

    def update_payment_network(self, users):
        """
        Update payment graph by adding new edge between users 1 and User 2.
        Input:
        :param user1: user making the payment
        :param user2: user receiving the payment

        :return:
            paymentGraph: updated graph with new edges added for new payment.
        """
        for user1 in users:
            for user2 in users:
                if user1 != user2:
                    # Check if Users1 had any transaction in past :
                    if user1 in self.__pay_graph:
                        # Check if user1 had transaction with user2:
                        if user2 not in self.__pay_graph[user1]:
                            # If NOT: Add user2 to connections of user 1.
                            self.__pay_graph[user1].append(user2)
                    else:
                        # If NOT add user1 to payment_graph
                        self.__pay_graph[user1] = [user2]

    def search_trusted_users(self, root_user):
        """
        This function generate a list of all users that are connected to root till degree 4.
        This is depth limited(4), queue-based implementation of Breadth First Search.

        :param root_user: user for whom trusted users needed to be found.

        :return:
            connection: a dictionary of users connected to root user at different degree.
            rootUser is at level 0 as it is origination of the search.
        """
        connection = {root_user: 0}  # connection to root users
        queue = deque()
        queue.append(root_user)

        while queue:
            node = queue.popleft()
            # restrict depth of search
            if connection.get(node, 5) < 4:
                for user in self.__pay_graph.get(node, []):
                    # check if node has been traversed
                    if user not in connection:
                        connection[user] = connection[node] + 1
                        queue.append(user)

        return connection

    def check_payment_status(self):
        """
        This function checks if incoming payment between two users is: TRUSTED or UNVERIFIED
        :param user1: user making the payment
        :param user2: user receiving the payment

        :return:
            Status: status of payment if TRUSTED or UNVERIFIED
        """
        # Find list of trusted users from payment graph for user1.
        users_trusted = self.search_trusted_users(self.user1)

        # check if user2 appears in Trusted users
        if self.user2 in users_trusted:
            # payment is trusted
            self.status = "trusted"
        else:
            # payment is unverified
            self.status = "unverified"

    def parse_row(self, row):
        """
        This function takes a row parsed from input file and extract fields.
        :param row: record read from input file .

        :return:
            timestamp - Timestamp of transaction    <type : time>
            user1 - user making the payment         <type : str>
            user2 - user receiving payments         <type : str>
            amount - amount of payment to be made   <type : Float>
        """
        # Extract fields from row:
        self.timestamp = int(time.mktime(time.strptime((row[0].strip()[0:10] + " " + row[0].strip()[12:]),
                                                  '%Y-%m-%d %H:%M:%S')))
        self.user1 = row[1].strip()
        self.user2 = row[2].strip()
        self.amount = float(row[3].strip())

    # -----------------------------------------------
    # STAGE 1: Batch Processing
    # -----------------------------------------------
    def batch_processing(self, batchfile):
        """
        This function will handle Stage 1 of our program i.e. Batch Processing,
        :param batchfile: a file containing records of payments between different users in past.

        :return: max_allowed_payment
        """
        with open(batchfile, 'r') as batch:
            field_batch = batch.readline()  # Column names in Batch File.
            batch_reader = csv.reader(batch)

            for row in batch_reader:
                try:
                    # Parse row read from batch file
                    self.parse_row(row)

                    # Add new edge for users making transaction in payment graph
                    self.update_payment_network(
                        users=[self.user1,self.user2]
                    )

                    # Find maximum amount of trusted payment in batch file
                    if self.amount > self.max_allowed_payment:
                        self.max_allowed_payment = self.amount

                except (IndexError, ValueError):
                    pass

    # -----------------------------------------------
    # STAGE 2: Stream Processing
    # -----------------------------------------------
    def stream_processing(self, streamfile, output1, output2, output3, output4):
        """
        This function reads stream of new payments. These challenge is to classify an incoming payment as "trusted" or
        "unverified" in order to avoid any fraudulent payments.
        :param streamfile, output1, output2, output3, output4

        Output: Generate output files with status of payment.
        """
        stream = open(streamfile, 'r')
        outputF1 = open(output1, 'w')
        outputF2 = open(output2, 'w')
        outputF3 = open(output3, 'w')
        outputF4 = open(output4, 'w')
        
        # open files:
        with stream, outputF1, outputF2, outputF3, outputF4:
            stream.readline()  # Column names in Stream File
            stream_reader = csv.reader(stream)
            for row in stream_reader:
                try:
                    # Read records from CSV file
                    self.parse_row(row)

                    # -------------------
                    # Core Features
                    # -------------------
                    # Check if the payment is TRUSTED or UNVERIFIED:
                    self.check_payment_status()

                    # ---------------------
                    # Additional Features
                    # ---------------------
                    # Check if the payment is TRUSTED or UNVERIFIED:
                    self.added_features_processing()
                    
                    # -----------------------------------------------
                    # STAGE 3: Write Status to output files.
                    # -----------------------------------------------
                    # Output1.txt
                    outputF1.write(self.status+"\n")
                    # Output2.txt
                    outputF2.write(self.status+"\n")
                    # Output3.txt
                    outputF3.write(self.status+"\n")
                    # Output4.txt
                    outputF4.write(self.report+"\n")

                except (IndexError, ValueError):
                    pass

    # --------------------------------------------
    # STAGE 4: Implementing ADDITIONAL FEATURES
    # --------------------------------------------
    def added_features_processing(self):
        """
        This function will check for any suspicious payment using additional features.
        :param user1(user making payment), user2(user requesting payment), ts(timestamp of payment)
        :return: Return the status of payment with
        """
        # Update payment heat graph for new payments 
        # -------------------------------------------
        active = self.added_features.update_heat_graph(self.timestamp, self.user1, self.user2)       
        
        # check for active payments
        if active:
            exceeded = self.amount > self.max_allowed_payment
            
            # Check if requested amount is more than maximum amount:
            if not exceeded:
                suspicious = self.added_features.check_if_suspicious([self.user1, self.user2])
                
                # Check for suspicious payments:
                if suspicious:
                    self.report = "Unverified \t Reason: Payment %s was suspicious, between users %s and %s" % \
                     (self.amount, self.user1, self.user2)
                
                else:
                    self.report = self.status     
            
            else:
                self.report = "Unverified \t Reason: Payment %s has exceeded maximum payment, between users %s and %s" % \
                     (self.amount, self.user1, self.user2)
        
        else:
            self.report = "Unverified \t Reason: Payment %s has expired, between users %s and %s" % \
                     (self.amount, self.user1, self.user2)
        
        
        
        '''
        # Step 4: Generate SuspiciousPaymentsReport:
        # --------------------------------------------------------------
        if not active:
            self.report = "Unverified \t Reason: Payment %s has expired, between users %s and %s" % \
                     (self.amount, self.user1, self.user2)
        elif suspicious:
            self.report = "Unverified \t Reason: Payment %s was suspicious, between users %s and %s" % \
                     (self.amount, self.user1, self.user2)
        elif exceeded:
            self.report = "Unverified \t Reason: Payment %s has exceeded maximum payment, between users %s and %s " % \
                     (self.amount, self.user1, self.user2)
        else:
            self.report = self.status
        '''

# ----------------------------------------------------
#       Main method :
# ----------------------------------------------------
def main(batchfile, streamfile, output1, output2, output3, output4):
    """
    Input:
        :param batchfile: batch file contains past transaction data. Used to build social network from payments
                         made between users.
        :param streamfile: stream of payments between users, check possibility of any fraudulent transactions
                        and classify a payment as - "trusted" or "unverified"
        :param output1: Output file for feature 1.
        :param output2: Output file for feature 2.
        :param output3: Output file for feature 3.
        :param output4: Output file for additional features implemented.

    Output: Classification of payments.
    """
    # call AntiFraud class
    anti_fraud = AntiFraud()

    # ----------------------------------------------------------------
    # STAGE 1: BATCH PROCESSING
    # Read batch file and generate payment_graph.
    # ----------------------------------------------------------------
    # get maximum allowed payment for stream payment.
    anti_fraud.batch_processing(batchfile)

    # -----------------------------------------------------------------------------
    # STAGE 2 : STREAM PROCESSING
    # Read stream of payments and classify payments as - "trusted" or "unverified"
    # -----------------------------------------------------------------------------
    anti_fraud.stream_processing(streamfile, output1, output2, output3, output4)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])