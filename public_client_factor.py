import koinex_public_client
import zebpay_public_client
import gdax_public_client
import bitfinex_public_client
import cex_public_client

class PublicClientFactor:
    @staticmethod
    def get_public_client(ex):
        if(ex == "gdax"):
            return gdax_public_client.GDAXPublicClient()
        elif(ex == "koinex"):
            return koinex_public_client.KoinexPublicClient()
        elif(ex == "zebpay"):
            return zebpay_public_client.ZebpayPublicClient()
        elif(ex == "bitfinex"):
            return bitfinex_public_client.BitfinexPublicClient()
        elif(ex == "cex"):
            return cex_public_client.CexPublicClient()