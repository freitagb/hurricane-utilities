from PIL import Image,ImageOps,ImageDraw,ImageFont
import glob
import os

atcfid = "al052019"
name = {"al062018": "Hurricane Florence",
        "al052019": "Hurricane Dorian"}
print(name.get(atcfid))
cwd = os.getcwd()

ir_path = '/'.join([cwd,atcfid,'images_grayscale/'])
cam_path = '/'.join([cwd,atcfid,'maps/'])
dvorak_path = '/'.join([cwd,atcfid,'images_dvorak/'])
predict_path = '/'.join([cwd,atcfid, 'predictions/'])
track_path = '/'.join([cwd,atcfid, 'track/'])

irs = sorted(glob.glob(ir_path + '*.png'))
cams = sorted(glob.glob(cam_path + '*.png'))
dvoraks = sorted(glob.glob(dvorak_path + '*.png'))
predictions = sorted(glob.glob(predict_path + '*.png'))
tracks = sorted(glob.glob(track_path + '*.png'))
stitched_image = Image.new('RGB',(5760,3240))

savedir = atcfid + '/stitched/'
for i in range(len(irs)):
    stitchedImageName = predictions[i].split('/')[-1].split('.png')[0]
    print(stitchedImageName)
    ir = Image.open(irs[i])
    cam = Image.open(cams[i])
    dvorak = Image.open(dvoraks[i])
    prediction = Image.open(predictions[i])
    track = Image.open(tracks[i])

    ir = ir.resize((1920,1920))
    cam = cam.resize((1920,1920))
    dvorak = dvorak.resize((1920,1920))
    prediction = prediction.resize((3840,1080))
    track = track.resize((1920,1080))
    pad = stitched_image.size[1] - (dvorak.size[1] + prediction.size[1])
    ir = ImageOps.expand(ir,border=(0,pad,0,0), fill='white') 
    cam = ImageOps.expand(cam,border=(0,pad,0,0), fill='white')
    dvorak = ImageOps.expand(dvorak,border=(0,pad,0,0), fill='white')

    stitched_image.paste(ir,(0,0))
    stitched_image.paste(cam,(ir.size[0],0))
    stitched_image.paste(dvorak,(2*ir.size[0],1))
    stitched_image.paste(prediction,(0,ir.size[1]))
    stitched_image.paste(track,(prediction.size[0],ir.size[1]))
    draw = ImageDraw.Draw(stitched_image)
    font = ImageFont.truetype("Avenir.ttc",160)
    textsize = font.getsize(name.get(atcfid))
    x = (stitched_image.size[0] - textsize[0])/2
    y = (stitched_image.size[1] - textsize[1])/2
    draw.text((x,40), name.get(atcfid), (0,0,0),font=font)
    #resized_image = stitched_image.resize((1920,1080))
    #resized_image.save(savedir + stitchedImageName + '.png')
    stitched_image.save(savedir + stitchedImageName + '.png')
    #stitched_image.close()


