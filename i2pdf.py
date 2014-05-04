#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import pygtk
import os

class App:
	wMain = None
	btnAdd = None
	btnConvert = None
	btnClear = None
	btnRemove = None
	lstFiles = None
	files = None
	imgPreview = None

	TARGETS = [
		('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
		('text/plain', 0, 1),
		('TEXT', 0, 2),
		('STRING', 0, 3),
		]

	def initUi(self):
		self.wMain = gtk.Window();
		self.btnAdd = gtk.Button("Přidat")
		self.btnAdd.connect("clicked", self.btnAdd_clicked)
		
		self.btnConvert = gtk.Button("Do PDF")
		self.btnConvert.connect("clicked", self.btnConvert_clicked)
		
		self.btnClear = gtk.Button("Vyčistit")
		self.btnClear.connect("clicked", self.btnClear_clicked)
		
		self.btnRemove = gtk.Button("Odebrat")
		self.btnRemove.connect("clicked", self.btnRemove_clicked)
		
		self.files = gtk.TreeStore(str)
		self.lstFiles = gtk.TreeView(self.files);
		self.lstFiles.connect("drag_data_get", self.lstFiles_ddGetData)
		self.lstFiles.connect("drag_data_received", self.lstFiles_ddReceivedData)
		self.lstFiles.connect("cursor-changed", self.lstFiles_Changed)
		self.lstFiles.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
		self.lstFiles.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT)
		
		self.imgPreview = gtk.Image()
		slPreview =  gtk.ScrolledWindow()
		slPreview.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		slPreview.add_with_viewport(self.imgPreview)
		
		self.wMain.connect("delete_event", self.wMain_delete)
		
		bbox = gtk.HButtonBox()
		bbox.add(self.btnAdd)
		bbox.add(self.btnClear)
		bbox.add(self.btnRemove)
		bbox.add(self.btnConvert)
		
		pMain = gtk.VBox(False)
		
		slFiles =  gtk.ScrolledWindow()
		slFiles.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		slFiles.add(self.lstFiles)
		
		tvcolumn = gtk.TreeViewColumn('Soubor')
		self.lstFiles.append_column(tvcolumn)
		cell = gtk.CellRendererText()
		tvcolumn.pack_start(cell, True)
		tvcolumn.add_attribute(cell, 'text', 0)
		
		#pMain.add(slFiles);
		#pMain.add(bbox)
		
		pLstImg = gtk.HPaned();
		pLstImg.add(slFiles)
		pLstImg.add(slPreview)
		
		# pMain.pack_start(slFiles, True, True, 0)
		pMain.pack_start(pLstImg, True, True, 0)
		pMain.pack_start(bbox, False, False, 0)
		
		self.updateUi()
		
		self.wMain.add(pMain)
		self.wMain.show_all()
	
	def lstFiles_Changed(self, tree_selection) :
		(tree_iter, value) = self.getSelectedFile()
		self.imgPreview.set_from_file(value)
		self.updateUi()
		
	def wMain_delete(self, widget, event, data=None):
		gtk.main_quit()
		return False
		
	def btnAdd_clicked(self, widget, data=None):
		files = self.getFiles()
		if files:
			for fileName in files:
				self.files.append(None, [fileName])
				
		self.updateUi()
	
	def btnClear_clicked(self, widget, data=None):
		self.files.clear()
		self.updateUi()
	
	def updateUi(self):
		exists = False
		for item in self.files:
			#print "neco"
			exists = True
			break
		
		self.btnConvert.set_sensitive(exists)
		self.btnClear.set_sensitive(exists)
		selected = False
		
		if exists :
			(model, pathlist) = self.lstFiles.get_selection().get_selected_rows()
			selected = len(pathlist) > 0
			
		self.btnRemove.set_sensitive(selected)
		
	def shellquote(self, s):
		return "'" + s.replace("'", "'\\''") + "'"
	
	def btnConvert_clicked(self, widget, data=None):
		dialog = gtk.FileChooserDialog(
			title = "Vyber PDF kam chceš uložit",
			action = gtk.FILE_CHOOSER_ACTION_SAVE,
			buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)
		)
		
		filter = gtk.FileFilter()
		filter.set_name("PDF dokument")
		filter.add_mime_type("application/pdf")
		filter.add_pattern("*.pdf")
		dialog.add_filter(filter)
		
		response = dialog.run()
		
		if response == gtk.RESPONSE_OK:
			fileName = dialog.get_filename()
			
		dialog.destroy()
		
		if response == gtk.RESPONSE_CANCEL:
			return
		
		if not fileName.lower().endswith(".pdf") :
			fileName = fileName + ".pdf"
			
		if os.path.exists(fileName):
			dialog = gtk.MessageDialog(
				parent=self.wMain, 
				type=gtk.MESSAGE_QUESTION, 
				buttons=gtk.BUTTONS_YES_NO, 
				message_format="Soubor existuje, opravdu chces prepsat soubor\n" + fileName
			)
			res = dialog.run()
			dialog.destroy()
			
			if res == gtk.RESPONSE_NO:
				return
				
		cmd = "convert "
		# print self.files.count
		for item in self.files:
			cmd = cmd + self.shellquote(item[0]) + " "
			
		cmd = cmd + self.shellquote(fileName)
		
		dialog = gtk.MessageDialog(
			parent=self.wMain, 
			type=gtk.MESSAGE_INFO, 
			buttons=gtk.BUTTONS_NONE, 
			message_format="Vytvářím PDF dokument\n" + fileName
		)
		dialog.show()
		os.system(cmd)
		#print cmd
		dialog.destroy()
		
		dialog = gtk.MessageDialog(
			parent=self.wMain, 
			type=gtk.MESSAGE_INFO, 
			buttons=gtk.BUTTONS_OK, 
			message_format="PDF dokument vytvořen\n" + fileName
		)
		dialog.run()
		dialog.destroy()
		
	def btnRemove_clicked(self, widget, data=None):
		#(model, pathlist) = self.lstFiles.get_selection().get_selected_rows()
		#for path in pathlist :
		#	tree_iter = model.get_iter(path)
		#	value = model.get_value(tree_iter,0)
		#	#print tree_iter
		#	#print value
		#	model.remove(tree_iter)
		(tree_iter, value) = self.getSelectedFile()
		model.remove(tree_iter)
		self.updateUi()
		
	def getSelectedFile(self):
		(model, pathlist) = self.lstFiles.get_selection().get_selected_rows()
		for path in pathlist :
			tree_iter = model.get_iter(path)
			value = model.get_value(tree_iter,0)
			
			return (tree_iter, value)
				
	def getFiles(self):
		dialog = gtk.FileChooserDialog(
			title = "Vyber obrázky ze kterých chceš udělat PDF",
			action = gtk.FILE_CHOOSER_ACTION_OPEN,
			buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
		)
		
		filter = gtk.FileFilter()
		filter.set_name("Obrázky")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_pattern("*.png")
		filter.add_pattern("*.jpg")
		filter.add_pattern("*.jpeg")
		filter.add_pattern("*.gif")
		filter.add_pattern("*.tif")
		filter.add_pattern("*.xpm")
		dialog.add_filter(filter)
		
		dialog.set_select_multiple(True)
				
		response = dialog.run()
		
		if response == gtk.RESPONSE_OK:
			files = dialog.get_filenames()

		elif response == gtk.RESPONSE_CANCEL:
			files = None
		
		dialog.destroy()
		
		return files
	
	def lstFiles_ddGetData(self, treeview, context, selection, target_id, etime):
		treeselection = treeview.get_selection()
		model, iter = treeselection.get_selected()
		data = model.get_value(iter, 0)
		selection.set(selection.target, 8, data)
		self.updateUi()
		
	def lstFiles_ddReceivedData(self, treeview, context, x, y, selection, info, etime):
		model = treeview.get_model()
		model = self.files
		data = selection.data
		drop_info = treeview.get_dest_row_at_pos(x, y)
		for line in data.split("\n"):
			if line[0:7] == 'file://' :
				line = line[7:]
			line = line.strip()
			if line != '':
				if drop_info:
					path, position = drop_info
					iter = model.get_iter(path)
					if (position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
						model.insert_before(iter, [line])
					else:
						model.insert_after(iter, [line])
				else:
					model.append(None, [line])
					if context.action == gtk.gdk.ACTION_MOVE:
						context.finish(True, True, etime)
		self.updateUi()
		return
							
if __name__ == "__main__":
	app = App()
	app.initUi()
	gtk.main()
