import protocol

if __name__ == "__main__":
    for i in range (1,10):
        cli = protocol.Client(9999)
        data = "networkkkkkkkkkkkkkkkkkk" + str(8*i) 
        data = bytes(data, 'utf-8') 
        print(data)
        fragmentation_size = 8       
        ttl_value = 64           

        cli.send(data, data_frag_len=fragmentation_size, ttl_func=lambda: ttl_value)
