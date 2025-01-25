import sys

from click import style
sys.path.append('.')
from tokenpdf.canvas import make_canvas, Canvas, CanvasPage, CanvasPageView
from tokenpdf.resources import ResourceLoader
import numpy as np


def paint_rotated_image(page):
    image = ResourceLoader().load_resource('https://picsum.photos/20/50')
    view : CanvasPageView = page.view(0,0, 100, 100)
    #view.image(0,0, 20, 50, image)

    # Rotate counter-clockwise by 30 degrees
    rview  = view.rotate(-np.pi * 30/180)
    rview.image(0,0, 20, 50, image)
    rview.line(0,0, 0, 100, style='dash')

    tview = page.view(20, 80, 80, 20)
    tview.image(0,0, 20, 50, image)
    tview.line(0,0, 0, 100, style='dash')

    rtview = tview.rotate(-np.pi * 30/180)
    rtview.image(0,0, 20, 50, image)
    rtview.line(0,0, 0, 100, style='dash')

def paint_rotated_line(page):
    view : CanvasPageView = page.view(0,0, 100, 100)
    view.line(0,0, 50, 100)
    view.line(0,0, 100, 100, style='dot-dash')
    rview = view.rotate(np.pi * 30/180)
    rview.line(0,0, 50, 50, style='dash')
    

    tview = page.view(20, 80, 80, 20)
    tview.line(0,0, 10, 10)
    rtview = tview.rotate(-np.pi * 30/180)
    rtview.line(0,0, 10, 10, style='dash')
    
def main():
    canvas : Canvas = make_canvas({'output_file':'test.pdf'})
    page = canvas.create_page([100,200])
    paint_rotated_image(page)
    #paint_rotated_line(page)


    canvas.save()


if __name__ == "__main__":
    main()