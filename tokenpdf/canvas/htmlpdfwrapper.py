
import asyncio
import time
from .canvas import ConvertCanvasWrapper






class HTMLPDFWrapper(ConvertCanvasWrapper):
    def __init__(self, subcanvas, config, file_path=None):
        super().__init__(subcanvas, config, file_path)
        self._psapp = None
    def convert(self, result, verbose:bool = False, return_result:bool = False):
        if return_result:
            raise NotImplementedError("Return result not implemented for HTMLPDFWrapper")
        converter = self.config.get("html2pdf_converter", "pyside6")
        if converter == "playwright":
            return self._convert_playwright(result, verbose)
        elif converter == "pyside6":
            return self._convert_pyside6(result, verbose)
        else:
            raise ValueError(f"Invalid converter: {converter}")
        
    def _convert_pyside6(self, result, verbose):
        from PySide6.QtCore import QTimer
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWidgets import QApplication
        
        import sys
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        view = QWebEngineView()
        view.setHtml(result)
        def save_pdf():
            view.page().printToPdf(self.file_path)
            view.page().pdfPrintingFinished.connect(lambda data: app.quit())
        last_change = [time.time()]
        def test_finished():
            if time.time() - last_change[0] > 1:
                save_pdf()
                return
            QTimer.singleShot(1000, test_finished)
        def keep_alive():
            last_change[0] = time.time()
        
        keep_alive()
        QTimer.singleShot(1000, test_finished)
        view.page().contentsSizeChanged.connect(keep_alive)
        view.show()
        app.exec_()
        

    
    def _convert_playwright(self, result, verbose):
        # import here to make sure playwright is imported in the main
        # thread first
        import playwright.async_api
        asyncio.run(HTMLPDFWrapper._convert_playwright_async(result, self.file_path, verbose))

    async def _convert_playwright_async(html, file_path, verbose=False):
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html)
            await page.pdf(path=file_path)
            await browser.close()

    @ConvertCanvasWrapper.converted_name.getter
    def converted_name(self):
        return "pdf(playwright)"