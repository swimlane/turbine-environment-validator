# # #!/usr/bin/env python3
# import turbine_environment_validator.lib.config as config
# import turbine_environment_validator.lib.log_handler as log_handler
#
# import OpenSSL.crypto
# from Crypto.Util import asn1
# import datetime
#
# logger = log_handler.setup_logger()
#
# def verify_certificate_key(cert, priv):
#
#     c=OpenSSL.crypto
#
#     pub = cert.get_pubkey()
#
#     # Only works for RSA (I think)
#     if pub.type()!=c.TYPE_RSA or priv.type()!=c.TYPE_RSA:
#         raise Exception('Can only handle RSA keys')
#
#     # This seems to work with public as well
#     pub_asn1=c.dump_privatekey(c.FILETYPE_ASN1, pub)
#     priv_asn1=c.dump_privatekey(c.FILETYPE_ASN1, priv)
#
#     # Decode DER
#     pub_der=asn1.DerSequence()
#     pub_der.decode(pub_asn1)
#     priv_der=asn1.DerSequence()
#     priv_der.decode(priv_asn1)
#
#     # Get the modulus
#     pub_modulus=pub_der[1]
#     priv_modulus=priv_der[1]
#
#     return pub_modulus == priv_modulus
#
# def get_certificate_info():
#     result = {
#         "swimlane_certificate" : {}
#     }
#
#     # The certificate - an X509 object
#     try:
#         cert = OpenSSL.crypto.load_certificate(
#                  OpenSSL.crypto.FILETYPE_PEM,
#                  open(config.arguments.swimlane_certificate).read()
#                )
#     except:
#         logger.error("Couldn't open {}, the file path my not exist, or it may not be an X509-encoded certificate.".format(config.arguments.swimlane_certificate))
#         result['swimlane_certificate']['expiration'] = "-"
#         result['swimlane_certificate']['message'] = "Couldn't open {}, the file path my not exist, or it may not be an X509-encoded certificate.".format(config.arguments.swimlane_certificate)
#         result['swimlane_certificate']['results'] = "{}Failed{}".format(config.FAIL, config.ENDC)
#         return result
#
#     # The private key - a PKey object
#     try:
#         priv = OpenSSL.crypto.load_privatekey(
#                  OpenSSL.crypto.FILETYPE_PEM,
#                  open(config.arguments.swimlane_key).read()
#                )
#     except:
#         logger.error("Couldn't open {}, the file path my not exist, or it may not be an X509-encoded certificate.".format(config.arguments.swimlane_key))
#         result['swimlane_certificate']['expiration'] = "-"
#         result['swimlane_certificate']['message'] = "Couldn't open {}, the file path my not exist, or it may not be an X509-encoded certificate.".format(config.arguments.swimlane_key)
#         result['swimlane_certificate']['results'] = "{}Failed{}".format(config.FAIL, config.ENDC)
#         return result
#
#     if verify_certificate_key(cert, priv):
#         result['swimlane_certificate']['expiration'] = '{}'.format( datetime.datetime.strptime(cert.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%SZ') )
#         result['swimlane_certificate']['message'] = "Certificate matches private key."
#         result['swimlane_certificate']['results'] = "{}Passed{}".format(config.OK, config.ENDC)
#     else:
#         result['swimlane_certificate']['expiration'] = "-"
#         result['swimlane_certificate']['message'] = "Certificate does not match private key."
#         result['swimlane_certificate']['results'] = "{}Failed{}".format(config.FAIL, config.ENDC)
#
#     return result