"""
    Author: Dhananjay Mehta (mehta.dhananjay28@gmail.com)
    Version: v1.0

    -----------------------------------------------------------
    INSIGHT DATA ENGINEERING CODING CHALLENGE: DIGITAL WALLET
    -----------------------------------------------------------

    C H A L L A N G E   S U M M A R Y  -

    This programs has been implemented to detect fraudulent payment requests from untrusted users using digital payment
    wallet. This program has been implemented in following stages with CORE and ADDITIONAL features:

    ADDITIONAL FEATURES: These are additional features crafted.
    ------------------------------------------------------------

    FEATURE 1: Payment heat graph.
    -------------------------------
    As payments stream in, I am generating a graph of payments made during a 60 seconds sliding window.
    This heat graph will help us identify users that are making a very high volume of payments in a short window.

    FEATURE 2: Expired payments
    -------------------------------
    Check if the payment requested is ACTIVE or EXPIRED.

    FEATURE 3: Payments exceeding maximum limit.
    ----------------------------------------------
    Check if a payment amount is exceeding limit of maximum amount.

"""


class AdditionalFeatures:
    """
    AdditionalFeatures class implements the additional features implemented to detect fraudulent transaction.
    Firstly, it builds a heat graph of payments during a 60 seconds window from incoming payments' stream.
    It will then chek for suspicious payment based on features created and write status report for any doubtful payment.
    """
    def __init__(self, h_graph=None):
        """
        initializes a objects of class.
        :param h_graph: dictionary of payments made between users and count of number of transaction between them.
        It represent graph of payments made in a sliding window of 60 seconds,
        """
        if h_graph is None:
            h_graph = {}
        self.__h_graph = h_graph

        self.payments_in_60sec = {}          # dictionary of payments in 60 seconds window with timestamp(ts) as key.
        self.timestamp_in_60sec = []         # list of timestamps in the 60 seconds sliding window.
        self.max_timestamp = -1              # timestamp of latest payments.
        self.active = None                   # payment is active initially
        self.suspected = False               # considering payment initially is not supicious

    def update_heat_graph(self, ts, user1, user2):
        """
        This function will update heat graph with new incoming payments. Heat graph will contain payment
        payments within last 60 seconds. Any payment before 60 seconds is purged.

        There are following conditions that need to be checked before the graph is updated:
            1. If incoming payment appears in order of timestamp.
            2. If incoming  payment is out of order of timestamp.
        :param ts: ts of incoming payment
        :param user1: user making payment
        :param user2: user initiating payment

        :return: Status of a payment as active or expired and updated heat graph.
        """
        # Step 1: check incoming payments:
        # --------------------------------
        # check if it is ACTIVE: i.e. if payment made in last two days
        # max timestamp - incoming timestamp < (2 * 86400) .
        if self.max_timestamp - ts < 172800:
            self.active = True
            
            # Check if payment arrives in order of timestamp-
            if ts >= self.max_timestamp:
                # Check if the timestamp is already in list - self.timestamp_in_60sec
                if ts != self.max_timestamp:
                    # append if not in the list.
                    self.timestamp_in_60sec.append(ts)
                    # update self.max_timestamp
                    self.max_timestamp = ts

                # check if already in payments_in_60Sec.
                if ts in self.payments_in_60sec:
                    # append incoming payments at given time
                    self.payments_in_60sec[ts].append([user1, user2])
                else:
                    # add the new payments at given time
                    self.payments_in_60sec[ts] = [[user1, user2]]

                # Step 2: Update the heat graph by adding new edge to h_graph
                # -------------------------------------------------------------
                self.add_graph_edge(
                    users=[user1, user2]
                )

                # Step 3: Delete edge from heat_graph for payments older than 60 seconds.
                # -----------------------------------------------------------------------
                while self.max_timestamp - self.timestamp_in_60sec[0] > 60:
                    # remove edge from heat map
                    self.delete_edge_graph()
                    # remove elements from payments_in_60sec for the timestamp
                    self.payments_in_60sec.pop(self.timestamp_in_60sec[0])
                    # remove the timestamp from list of last 60 seconds
                    self.timestamp_in_60sec.pop(0)

            # If payment does not arrive in order:
            else:
                # Check if incoming payment is in last 60 Seconds
                if self.max_timestamp - ts <= 60:
                    
                    # find index to insert the new payment in the sliding window
                    index = bisect.bisect_left(self.timestamp_in_60sec, ts)
                    if (ts != self.timestamp_in_60sec[index]):
                        self.timestamp_in_60sec.insert(index, ts)

                    # Check if timestamp is in list of timestamps
                    if ts not in self.timestamp_in_60sec:
                        self.timestamp_in_60sec.append(ts)

                    # Check if ts already in payments60Sec
                    if ts in self.payments_in_60sec:
                        self.payments_in_60sec[ts].append([user1, user2])
                    else:
                        self.payments_in_60sec[ts] = [[user1, user2]]

                    # Update the heat graph for new payment.
                    self.add_graph_edge(users=[user1, user2])

                # Check if incoming payment is older than 60 Seconds
                else:
                    pass
        else:
            # if incoming payment is older than 2 days:
            self.active = False
                    
        return self.active

    def add_graph_edge(self, users):
        """
        This function adds edges to the heat graph.
        :param users: list of users (user1 and user2 ) that will form edge in the graph.

        :return:
            graph  - updated heat graph with new edges from new payments by users.
        """
        # for both the users in users list
        for user1 in users:
            for user2 in users:
                if user1 != user2:
                    # if user1 exist for user2 in current graph
                    if user1 in self.__h_graph:
                        # check if user2 is connected to user1
                        if user2 in self.__h_graph[user1]:
                            # increase number of payments that connect user1 and user2
                            self.__h_graph[user1][user2] += 1
                        # if user2 does not exist for user1 in current graph
                        else:
                            self.__h_graph[user1][user2] = 1
                    # if user1 does not exist in graph at all: Add user1 to graph
                    else:
                        self.__h_graph[user1] = {user2: 1}

    def delete_edge_graph(self):
        """
        This function deletes edges from heat graph for payments made before 60 seconds.
        :return:
            graph - updated heat graph with edges from payments that happened before 60 seconds window.
        """
        for users in self.payments_in_60sec[self.timestamp_in_60sec[0]]:
            # check if there are users for current timestamp to delete
            for user1 in users:
                for user2 in users:
                    if user2 != user1:
                        # reduce count of connecting edges between user1 and user2:
                        self.__h_graph[user1][user2] -= 1
                        # if user1 and user2 are no longer connected:
                        if self.__h_graph[user1][user2] == 0:
                            # remove user2 from connection of user1:
                            self.__h_graph[user1].pop(user2)
                            # if user1 is not connected to any other user:
                            if self.__h_graph[user1] == {}:
                                # remove user1 from heat graph:
                                self.__h_graph.pop(user1)

    def check_if_suspicious(self, users):
        """
        This function checks if an incoming payment looks suspicious.
        A payment is SUSPICIOUS if:
            - if user1 or user2 have significantly large transactions with other user in last 60 seconds.
            - if user1 and user2 have large number of transactions between them in last 60 seconds.
            NOTE: I have set limit for suspicious transactions as >100 in 60 seconds; this can be increased or decreased
                as per requirement in future.

        :param users: list of two users[user1, user2] between who payment needs to be checked

        :return:
                suspected: boolean value indicating if a payment is suspicious or not.
        """
        for user1 in users:
            for user2 in users:
                if user2 != user1:
                    # if user 1 has any payment in last 60 seconds
                    if user1 in self.__h_graph:
                        # if user1 have many transactions in less than 60 seconds: e.g.10 with different user 
                        if len(self.__h_graph[user1]) > 10:
                            self.suspected = True
                        # if user1 has large number of transactions with user2
                        elif user2 in self.__h_graph[user1] and self.__h_graph[user1][user2] > 10:
                            self.suspected = True

        return self.suspected