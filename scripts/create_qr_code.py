import qrcode

print("qrcode package imported properly")

code = qrcode.make("ENPM 701!")
code.save("enpm701qrcode.png")
print("QR code generated & saved")

