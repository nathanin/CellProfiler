import wx
import wx.lib.scrolledpanel


class ScrollableText(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, identifier=-1, text=None):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, identifier)

        if text is None:
            text = [[('black', 'adsf')]]
        self.SetVirtualSize((1500, 1500))
        self.SetupScrolling(True, True)

        # a list of lists of (color, string) tuples
        self.Bind(wx.EVT_PAINT, self.redraw)
        self.Bind(wx.EVT_SIZE, self.resize)

        # setup the font
        self.font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
        if not self.font.IsFixedWidth():
            self.font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL)
        assert self.font.IsFixedWidth()

        self.text = text
        self.set_longest_line()

    def set_text(self, text):
        self.text = text
        self.set_longest_line()
        self.resize(None)
        self.Refresh()

    def set_longest_line(self):
        if len(self.text) > 0:
            self.longest_line = max([sum([len(s) for c, s in l]) for l in self.text])
        else:
            self.longest_line = 1

    def draw_lines(self, DC, start, end, lineheight):
        mw = 0
        DC.SetFont(self.font)
        for idx in range(max(0, start), min(end, len(self.text))):
            l = self.text[idx]
            combined = "".join([s[1] for s in l])
            extents = [0] + DC.GetPartialTextExtents(combined)
            for string in l:
                DC.SetTextForeground(string[0])
                DC.DrawText(string[1], extents[0], idx * lineheight)
                extents = extents[len(string[1]):]

    def resize(self, evt):
        DC = wx.ClientDC(self)
        DC.SetFont(self.font)

        # find line width and  height
        extent = DC.GetFullTextExtent('X' * self.longest_line)
        lineheight = extent[1]
        maxwidth = extent[0]

        # set virtual area
        vsize = (maxwidth, len(self.text) * lineheight)
        if self.GetVirtualSize() != vsize:
            self.SetVirtualSize(vsize)

    def redraw(self, evt):
        DC = wx.PaintDC(self)
        self.PrepareDC(DC)
        extent = DC.GetFullTextExtent('x' * self.longest_line)
        lineheight = extent[1]
        vs = self.GetViewStart()
        ppu = self.GetScrollPixelsPerUnit()
        ri = wx.RegionIterator(self.GetUpdateRegion())
        mmin, mmax = len(self.text), 0
        while ri:
            rect = ri.GetRect()
            # find the lines that need rendering
            min_y = rect[1] + vs[1] * ppu[1]
            max_y = rect[1] + rect[3] + vs[1] * ppu[1]
            min_line = int(min_y / lineheight) - 1
            max_line = int(max_y / lineheight) + 2
            mmin = min(min_line, mmin)
            mmax = max(max_line, mmax)
            ri.Next()
        self.draw_lines(DC, mmin, mmax, lineheight)
