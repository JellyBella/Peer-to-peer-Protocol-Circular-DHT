Implementation of the peer-to-peer (P2P) protocol Circular DHT

Background

The following is extracted from the Peer Churn section of the text:
In P2P systems, a peer can come or go without warning. Thus, when designing a DHT, we also must be concerned about maintaining the DHT overlay in the presence of such peer churn. To get a big-picture understanding of how this could be accomplished, let’s once again consider the DHT in Figure 2.27(a) [Reproduced here as Figure 1]. To handle peer churn, we will now require each peer to track (that is, know the IP address of) its first and second successor; for example, peer 4 now tracks both peer 5 and peer 8. We also require each peer to periodically verify that its two successors are alive (for example, by periodically sending ping messages to them and asking for responses). Let’s now consider how DHT is maintained when a peer abruptly leaves. For example, suppose peer 5 in Figure 2.27(a)[Figure 1 in this assignment spec] abruptly leaves. In this case, the two peers preceding the departed peer (4 and 3) learn that 5 has departed, since it no longer responds to ping messages. Peers 4 and 3 thus need to update their successor state information. Let’s consider how peer 4 updates its state:
1. Peer 4 replaces its first successor (peer 5) with its second successor (peer 8).
2. Peer 4 then asks its new first successor (peer 8) for the identifier and IP addresses of its immediate successor (peer 10). Peer 4 then makes peer 10 its second successor.
Having briefly addressed what has to be done when a peer leaves, let’s now consider what happens when a peer wants to join the DHT. Let’s say a peer with identifier 13 wants to join the DHT, and at the time of joining, it only knows about peer 1’s existence in the DHT. Peer 13 would first send peer 1 a message, saying ”what will be peer 13’s predecessor and successor?” This message gets forwarded through the DHT until it reaches peer 12, who realises it will be peer 13’s predecessor and its current successor, peer 15, will become its successor. Next, peer 12 sends this predecessor and successor information to peer 13. Peer 13 can now join the DHT by making peer 15 its successor and by notifying peer 12 that it should be its immediate successor to peer 13.

Brief description

Step 1: Ping successors
Function pingRequest() keeps on sending ping request messages with “relation”(sent to 1st or 2nd successor), “count”(the sequence number), current PeerID and “request” to indicate this is request message to successor 1 and 2. 

Function pingResponse() accepts request sent by pingRequest() from its predecessors, and send back response messages with “relation”, “ack”(acknowledge sequence number), PeerID and “response”. Meanwhile, if peer hasn’t know predecessors’ address or the changes of predecessors’ address, it helps to update address.
And two functions run in threads separately so that they can process at the same time, sending and receiving individually.

Function PortNum() transfers port number i(can be string sometimes) to address(int, 50000+i).

Step 2: Requesting a file
In main code(outside functions), using loop to get user input continually and check if current peer or the next peer has the file, if neither of them has the file, just pass on it to the next successor and check again later on.  

Function TCPRequest(senderpeer, filenum, func) run different functions for different situation listed above by using 3 parameters. The 1st parameter senderpeer is the origin peer which requires the file, 2nd parameter is the file number and the last parameter tells current peer what to do. For example, when current peer has the file, just printed out “File NUM is here”. When successor 1 has the file, not only send messages to successor but also tell it has the file.

Function check() helps to compute the hash of a file and which peer might has the file

Function TCPResponse() creates a new socket and binds address to current peer and start listen to other peers’ messages. And runs different functions according to received message. For example, if messages indicates current peer has the file then print out and send the file to origin sender. If the former peer has no idea who has the file(which means former and current peer don’t have the file, file must be in one of the later ports) in former check, it checks again in current peer(similar process in main check).   

Step 3: Peer departure
If user input “quit ”, which activates function TCPRequest() again for sending messages to predecessor 1 and 2 and successor 1 and 2 the message that peer departs and meanwhile send new successors’ address to predecessors and new predecessors’ address to successors. So that after departing, all peers related to current peer got information about new successors and predecessors. And TCPResponse() after receiving new addresses, it updates addresses according to different roles they are to departed peer. And new ports will be printed out in prompt after updates.

Step 4: Kill a peer
Because when peer is killed by user ungracefully, there is no chance for it to send warning messages to its related peers(predecessors and successors). So by calculating the gap between sequence numbers in request messages and acknowledge sequence numbers in response messages for both successors, if the gap is bigger than 4, the peer knows one of its successors leaving the network. So it updates the remaining successor as successor 1(or if successor 1 remains, stay the same) and inquire successor 1 for its 1st successor, which will be updated to current peer’s successor 2. Everytime when successors are updated, gap and sequence number will be recalculated so that it won’t be affected by old informations
