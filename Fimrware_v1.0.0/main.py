 # pyinstaller --onefile -w main.py

 # #################################################################################################################################################################
 # Comandos avrdude
 #
 # Bootloader (attiny13):
 # avrdude -u -c " & upload_prog & " -p " & upload_chip & " -P " & upload_port & " -b 19200 -F -v -v -U lock:w:0x3F:m -U hfuse:w:0b11111011:m -U lfuse:w:0x7A:m"
 # comando = f"avrdude -u -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U lock:w:0x3F:m -U hfuse:w:0b11111011:m -U lfuse:w:0x7A:m"
 # Bootloader (atmega8, atmega328, attiny85):
 # avrdude -c " & prog & " -p " & upload_chip & " -P " & port & " -b 19200 -F -v -v -U flash:w:" & upload_file & ":a"
 # comando = f"avrdude -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U flash:w:{upload_file}:a"
 #
 # Sketch.hex (atmega8, atmega328, attiny13, attiny85):
 # avrdude -c " & upload_prog & " -p " & upload_chip & " -P " & upload_port & " -b 19200 -F -v -v -U flash:w:" & upload_file & ":a"
 # comando = f"avrdude -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U flash:w:{upload_file}:a"
 #
 # Lock (atmega8, atmega328, attiny13, attiny85):
 # avrdude -u -c " & upload_prog & " -p " & upload_chip & " -P " & upload_port & " -b 19200 -F -v -v -U lock:w:" & upload_lock & ":m"
 # comando = f"avrdude -u -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U lock:w:{upload_lock}:m"
 #
 # #################################################################################################################################################################
 # Lock bits:
 
 # atmega8: 0x0C
 # atmega328: 0x0C
 # attiny13: 0x3C
 # attiny85: 0xFC
 #
 # #################################################################################################################################################################
 

import customtkinter as ctk
from customtkinter import filedialog
from PIL import Image
from pathlib import Path
import serial
import serial.tools.list_ports
import threading
import subprocess
import time
import os
import PIL.Image

# Lista de chips
chips = []
chips.extend(["atmega328", "atmega8", "attiny13", "attiny85"])

# Lista de programadores
progs = []
progs.extend(["ArduinoISP", "Arduino", "UsbAsp"])

# Inicialização do customtkinter
ctk.set_appearance_mode("dark")  # Define o modo de aparência (dark/light/system)
ctk.set_default_color_theme("blue")  # Define o tema de cor

# Variável para controle
new_fonte = ("Courier New", 12)
upload_prog = None
upload_chip = None
upload_port = None
upload_baud = None
upload_file = None
upload_boot = None
upload_lock = None
comando = None
#comando = f"avrdude -u -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U lock:w:{upload_lock}:m"
#          avrdude -u -c Arduino -p t85 -P COM5 -b 19200 -F -v -v -U lock:w:0xFC:m"

# Função para listar portas COM ativas
def list_portas():
    return [port.device for port in serial.tools.list_ports.comports()]

# Função para atualizar a combobox com as portas disponíveis
def scan_port_combo():
    com_port_combo.set('')  # Limpa o texto selecionado da combobox
    portas = list_portas()
    com_port_combo.configure(values=portas)  # Atualiza os valores da combobox
    if portas:
        com_port_combo.set(portas[0])  # Seleciona a primeira porta, se houver

def search_file():
    text_file.configure(state='normal')  # Habilita texto para file
    # Abre a caixa de diálogo para selecionar um arquivo
    file_select = filedialog.askopenfilename(filetypes=(("Arquivos hexadecimais", "*.hex"), ("", "")))
    # Se um arquivo for selecionado, atualiza o campo de texto
    text_file.delete(0, ctk.END) # Limpa o campo de texto
    text_file.insert(0, file_select) # Insere o caminho do arquivo selecionado no campo de texto
    text_file.configure(state='disabled')  # Desbilita texto para file

# Função chamada quando o estado da checkbox é alterado
def on_checkbox1_toggle():
    # BOOTLOADER
    # Se checkbox lock selecionado
    if checkbox_var1.get() == 1 and checkbox_var2.get() == 0 :
        checkbox_var3.set(0)  # Desmarca Lock
    if checkbox_var2.get() == 1 and text_file.get() == "" :
        upload_cmd_button.configure(state='disabled')
    if checkbox_var2.get() == 0 :
        upload_cmd_button.configure(state='normal')
    # Nenhum checkbox selecionado
    if checkbox_var1.get() == 0 and checkbox_var2.get() == 0 and checkbox_var3.get() == 0 :
        upload_cmd_button.configure(state='disabled')
     # Se programdor selecionado for "Arduino"
    if prog_select_combo.get() == "Arduino" :
        checkbox_var1.set(0)  # Desmarca Bootloader

def on_checkbox2_toggle():
    # SKETCH
    if checkbox_var1.get() == 1 and checkbox_var2.get() == 0 :
        checkbox_var3.set(0)  # Desmarca Lock
    # Nenhum checkbox selecionado
    if checkbox_var1.get() == 0 and checkbox_var2.get() == 0 and checkbox_var3.get() == 0 :
        upload_cmd_button.configure(state='disabled')
    else:
        upload_cmd_button.configure(state='normal')
    # Se checkbox sketch selecionado e texto file em branco
    if checkbox_var2.get() == 1 and text_file.get() == "" :
        upload_cmd_button.configure(state='disabled')
    # Se programdor selecionado for "Arduino"
    if prog_select_combo.get() == "Arduino" :
        checkbox_var1.set(0)  # Desmarca Bootloader
        checkbox_var3.set(0)  # Desmarca Lock

def on_checkbox3_toggle():
    # LOCK
    if checkbox_var1.get() == 1 and checkbox_var2.get() == 0 :
        checkbox_var3.set(0)  # Desmarca Lock
    if checkbox_var2.get() == 1 and text_file.get() == "" :
        upload_cmd_button.configure(state='disabled')
    if checkbox_var1.get() == 0 and checkbox_var2.get() == 0 :
        upload_cmd_button.configure(state='normal')
    # Nenhum checkbox selecionado
    if checkbox_var1.get() == 0 and checkbox_var2.get() == 0 and checkbox_var3.get() == 0 :
        upload_cmd_button.configure(state='disabled')
    # Se programdor selecionado for "Arduino"
    if prog_select_combo.get() == "Arduino" :
        checkbox_var3.set(0)  # Desmarca Bootloader

def send_command():
    text_dados.configure(state='normal')
    # Limpa área de texto de dados e comando
    text_dados.delete("1.0", "end")
    text_dados.update_idletasks()
    text_cmd.delete("1.0", "end")
    text_cmd.update_idletasks()
        
    # Atualiza a variável upload_prog
    if prog_select_combo.get() == "ArduinoISP" :
        upload_prog = "Arduino"
        upload_baud = "19200"
    elif prog_select_combo.get() == "Arduino" :
        upload_prog = "Arduino"
        upload_baud = "115200"
    elif prog_select_combo.get() == "UsbAsp" :
        upload_prog = "usbasp"
        upload_baud = "19200"
    
    # Atualiza a variável upload_chip e upload_lock
    if chip_select_combo.get() == "atmega328" :
        upload_chip = "m328p"
        upload_lock = "0x0C"
    elif chip_select_combo.get() == "atmega8" :
        upload_chip = "m8"
        upload_lock = "0x0C"
    elif chip_select_combo.get() == "attiny13" :
        upload_chip = "t13"
        upload_lock = "0x3C"
    elif chip_select_combo.get() == "attiny85" :
        upload_chip = "t85"
        upload_lock = "0xFC"
        
    # Atualiza a variável upload_port
    upload_port = com_port_combo.get()
    
    # Atualiza a variável upload_file
    upload_file = text_file.get()
    
    # Atualiza a variável upload_boot
    chip = chip_select_combo.get()
    get_bootloader_file(chip)
    if not os.path.exists(upload_boot):
        text_dados.insert("end", f"Não possivel encontrar o arquivo {upload_boot}\n")
        text_dados.update_idletasks()
   
    # Executa comando selecionado
    try:        
        # BOOTLOADER
        if checkbox_var1.get() == 1:            
            if chip_select_combo.get() == "atmega8" or chip_select_combo.get() == "atmega328":
                comando = f"avrdude -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U lfuse:w:0xF7:m -U hfuse:w:0xD7:m -U efuse:w:0xFD:m -U lock:w:0xFF:m -U flash:w:{upload_boot}:a"
            elif chip_select_combo.get() == "attiny13":
                comando = f"avrdude -u -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U lock:w:0x3F:m -U hfuse:w:0b11111011:m -U lfuse:w:0x7A:m"
            elif chip_select_combo.get() == "attiny85":
                comando = f"avrdude -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U lfuse:w:0xF1:m -U hfuse:w:0xDF:m -U efuse:w:0xFF:m -U lock:w:0xFF:m -U flash:w:{upload_boot}:a"
            status_process(comando)   
            
        # SKETCH
        if checkbox_var2.get() == 1:
            comando = f"avrdude -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b {upload_baud.strip()} -F -v -v -U flash:w:{upload_file}:a"
            status_process(comando)
                
        # LOCK
        if checkbox_var3.get() == 1:
            comando = f"avrdude -u -c {upload_prog.strip()} -p {upload_chip.strip()} -P {upload_port.strip()} -b 19200 -F -v -v -U lock:w:{upload_lock}:m"
            status_process(comando)
            
    except subprocess.CalledProcessError as e:
        text_dados.insert("end", f"O comando falhou com o código {e.returncode}.\n")
        text_dados.update_idletasks()
        #print(f"O comando falhou com o código {e.returncode}.")
        #print(e.output)

    text_dados.configure(state='disabled')

def status_process(comando):
    text_cmd.delete("1.0", "end")
    text_cmd.insert("end", comando)
    processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for linha in processo.stderr:
        # Decodifica a linha para texto
        linha = linha.decode("utf-8").strip()
        text_dados.insert(ctk.END, linha + "\n")
        text_dados.see(ctk.END)  # Faz com que a nova linha fique visível
        text_dados.update_idletasks()

def send_command_extern():
    text_dados.configure(state='normal')
    text_dados.delete("1.0", "end")
    text_dados.update_idletasks()
    comando = text_cmd.get('1.0', 'end-1c')
    processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for linha in processo.stderr:
        # Decodifica a linha para texto
        linha = linha.decode("utf-8").strip()
        text_dados.insert(ctk.END, linha + "\n")
        text_dados.see(ctk.END)  # Faz com que a nova linha fique visível
        text_dados.update_idletasks()
    text_dados.configure(state='disabled')

def get_bootloader_file(chip):
    global upload_boot
    upload_boot = os.path.join(os.getcwd(), f"bootloader_{chip}.hex")

def prog_select(event):
    # Se programdor selecionado for "Arduino"
    if prog_select_combo.get() == "Arduino" :
        checkbox_var1.set(0)  # Desmarca Bootloader
        checkbox_var3.set(0)  # Desmarca Lock
                 
# Interface CustomTkinter
root = ctk.CTk()
root.title("Avrdude-GUI")
root.geometry("850x560")

# Frame para configurações
frame_port = ctk.CTkFrame(root)
frame_port.pack(pady=10)
frame_file = ctk.CTkFrame(root)
frame_file.pack(pady=0)
frame_text = ctk.CTkFrame(root)
frame_text.pack(pady=10)

# Carregue a imagem com PIL e crie um CTkImage
image = Image.open("Logo.bmp")
ctk_image = ctk.CTkImage(image, size=(820, 120))  # Ajuste o tamanho conforme necessário

# Crie um CTkLabel dentro do frame para exibir a imagem
label_image = ctk.CTkLabel(frame_text, image=ctk_image, text="")
label_image.grid(row=2, column=0, pady=5)

# ComboBox para chip select
chip_select_combo = ctk.CTkComboBox(frame_port, font=new_fonte, values=chips, width=125, state="readonly")
chip_select_combo.grid(row=0, column=0, padx=10, pady=10)
chip_select_combo.set(chips[0])  # Seleciona o primeiro chip da lista

# ComboBox para prog select
prog_select_combo = ctk.CTkComboBox(frame_port, font=new_fonte, values=progs, command=prog_select, width=125, state="readonly")
prog_select_combo.grid(row=0, column=1, padx=0, pady=10)
prog_select_combo.set(progs[0])  # Seleciona o primeiro chip da lista

# ComboBox para portas COM
com_port_combo = ctk.CTkComboBox(frame_port, font=new_fonte, values=list_portas(), width=80, state="readonly")
com_port_combo.grid(row=0, column=2, padx=10, pady=10)
scan_port_combo() # Atualiza as portas COM no combo

# Botão para scanear portas
scan_port_button = ctk.CTkButton(frame_port, font=new_fonte, text="Scan", command=scan_port_combo, width=100)
scan_port_button.grid(row=0, column=3, padx=0, pady=10)

# Variável associada à checkbox para guardar seu estado (0 = desmarcado, 1 = marcado)
checkbox_var1 = ctk.IntVar(value=0) # Bootloader
checkbox_var2 = ctk.IntVar(value=0) # Sketch.hex
checkbox_var3 = ctk.IntVar(value=0) # Lock

# Criação das checkbox
checkbox1 = ctk.CTkCheckBox(frame_port, font=new_fonte, text="Bootloader", variable=checkbox_var1, command=on_checkbox1_toggle)
checkbox1.grid(row=0, column=4, padx=10, pady=10)
checkbox2 = ctk.CTkCheckBox(frame_port, font=new_fonte, text="Sketch.hex", variable=checkbox_var2, command=on_checkbox2_toggle)
checkbox2.grid(row=0, column=5, padx=10, pady=10)
checkbox3 = ctk.CTkCheckBox(frame_port, font=new_fonte, text="Lock", variable=checkbox_var3, command=on_checkbox3_toggle)
checkbox3.grid(row=0, column=6, padx=10, pady=10)

#Área de texto para sketch.hex
text_file = ctk.CTkEntry(frame_file, font=new_fonte, width=600)
text_file.grid(row=1, column=0, padx=5, pady=10)
text_file.configure(state='disabled')

# Botão para buscar sketch.hex
search_file_button = ctk.CTkButton(frame_file, font=new_fonte, text="File", command=search_file, width=100)
search_file_button.grid(row=1, column=1, padx=5, pady=10)

# Botão para enviar upload
upload_cmd_button = ctk.CTkButton(frame_file, font=new_fonte, text="Upload", command=send_command, width=100)
upload_cmd_button.grid(row=1, column=2, padx=5, pady=10)
upload_cmd_button.configure(state='disabled')

# Área de texto para exibir dados 
text_dados = ctk.CTkTextbox(frame_text, font=new_fonte, width=820, height=250)
text_dados.grid(row=0, column=0, padx=5, pady=5)
text_dados.configure(state='disabled')

# Área de texto para exibir comandos
text_cmd = ctk.CTkTextbox(frame_text, font=new_fonte, width=820, height=20)
text_cmd.grid(row=1, column=0, padx=5, pady=0)

# Enter para enviar comandos externos
text_cmd.bind('<Return>', lambda event: send_command_extern())

root.mainloop()
