# TIE-02101 Ohjelmointi 1
# Rauli Virtanen, rauli.virtanen@tuni.fi, opiskelijanumero: 290592
# Tehtävä: Oman GUI:n suunnittelu ja toteutus
# Ohjelman kuvaus: StudyTimer - opiskeluajankäytönhallintatyökalu
#
# Kielivalinnoista: Koodi on toteutettu englanniksi, mutta UI, tämä
# dokumentaatio ja käyttöohjeet ovat suomeksi. Opiskeltavat kurssit sekä
# niihin liittyvät kuvat ovat suomenkielisiä, joten suomenkielinen UI tuntui
# loogiselta.
#
# Olen tähdännyt skaalautuvaan versioon projektista
#
# Käyttöohjeet löytyvät alta koodista "guide()" sekä itse ohjelmasta: Help ->
# Ohjeet. Tässä header dokumentaatiossa keskityn teknisen toteutuksen
# kuvailemiseen
#
# Tärkeimmät tietorakenteet:
#
# Subject: Opiskeltavan aineen luokka, joka pitää sisällään tiedot sen kurssin
# kuvakkeesta, buttonista, labelista sekä niiden sijoittelusta. Lisäksi se
# sisältää tiedon aloitus- ja lopetusajasta sekä kurssin opiskeluun käytetystä
# kokonaisajasta kuten myös tiedon siitä, onko nappi päällä vai ei.
# Metodit ovat varsin suoraviivaisia tiedon talletus/haku/muutos funktioita.
# Luokan parametrit ovat napin paikka ja kurssin kuvakkeen tiedostonimi.
#
# Koodissa on lisäksi kaksi muuta luokkaa. Toinen vieritettävien ikkunoiden
# luomiseen ja toinen itse käyttöliittymää varten.
#
# __subjects_to_be_studied on sanakirja, joka sisältää  luokan Subject oliot
# muodossa {kurssin tunnus:olio}
#
# __previous_studies on sanakirja, avaimenaan päivämäärä ja arvonaan lista
# sanakirjoja, mitä sinä päivänä on opiskeltu, muotonaan niin ikään sanakirja
# {kurssi:käytetty aika sekunteina}
# Eli kokonaisuudessaan: {pvm:[{kurssi1:aika1}, {kurssi2:aika2}….]}
# Ladatut tiedot tallenetaan tähän sanakirjaan. Samoin siihen päivitetään
# kaikki muutokset ennen isompien toiminnallisuuksien toteuttamista.
# Myös tallennus tapahtuu tämän rakenteen kautta tietojen päivityksen jälkeen.
#
# Ohjelmaa on vaikea käyttää virheellisesti, kuten tekijäänsäkin.
# Virheilmoitukset koskevat tiedostonkäsittelyä ja halua näyttää
# opintosuoritukset jos opintosuorituksia ei ole.
#
# Toimiakseen ohjelma vaatii tiedoston "config.cfg", joka sisältää
# objektien tiedot muodossa: kurssin id, kuvaketiedoston nimi, nappijärjestys.
#
# Tallennus ja lataus tapahtuu .stf -tiedoston kautta. Tiedostossa jokainen
# rivi vastaa tiettyä päivämäärää. Päivämäärän määrittää opiskelujen
# päättymishetki. Tiedosto on muodossa: ppkkvvvv;kurssi1:aika1,kurssi2:aika2...
#
# Ajatus ohjelmaan sai alkunsa Wordiin tekemästäni manuaalisesta
# opiskelupäiväkirjasta. Entisestään sitä ruokki osallistuminen
# älysormustutkimukseen, joka myös edellytti opintosessioiden kirjaamista.
#
# Jatkossa (ehkä jollain myöhemmällä kurssilla) käytettävyyttä voisi parantaa
# kääntämällä ohjelma mobiilisovellukseksi, mieluiten WatchOS:lle. Lisäksi
# kursseille voisi lisätä eri osa-alueita ja tallentaa opiskeluun käytetyt
# kellonajat. Kalenterirajapinta mahdollistaisi opiskelujen viemisen omaan
# kalenteriinsa värikoodattuna. Myös kalenterin lukujärjestyksestä voisi tuoda
# tietoa ohjelmaan siten, että se osaisi ehdottaa lukujärjestyksen mukaista
# opiskelutapahtumaa.
#
# Ohjelma sopisi sinällään myös asiakaslaskutukseen. Lisänä voisi olla mm.
# puhelinlogien yhdistäminen laskutukseen, kun asiakas on löydettävissä
# puhelinnumeron perusteella.


from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import datetime
import time
import calendar
import platform


# Class to create scrollable frame
class Scrollable(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        # Configuring textbox and scrollbar elements
        self.text = Text(self, height=15, width=50)
        self.sb = Scrollbar(self, orient="vertical", command=self.text.yview)

        # Scrollable in y -axis
        self.text.configure(yscrollcommand=self.sb.set, font=("times", 16))

        # And packing them up for the view
        self.sb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)


    def print_about(self, i, to_print):

        # Align given text in center and print it to textbox
        self.text.tag_configure("center", justify='center')
        self.text.tag_add("center", 1.0, "end")

        # Make textbox editable before inserting the line and disable editing
        # after printing it
        self.text.configure(state="normal")
        self.text.insert("end", to_print[i] + "\n", "center")
        self.text.configure(state="disabled")

        # For every line until eof
        if i < len(to_print)-1:
            # print line, wait for (1000ms), and print next line increasing
            # index of lines as the function is called from itself.
            self.after(1000, lambda o=i: self.print_about(o + 1, to_print))



    def print_guide(self, to_print):
        # Insert guide (= to_print) to the textbox line by line aligned center
        for line in to_print:
            self.text.tag_configure("center", justify="center")
            self.text.tag_add("center", 1.0, "end")
            self.text.insert("end", line + "\n", "center")
        self.text.configure(state="disabled")


# CLASS FOR THE SUBJECTS TO BE STUDIED
class Subject:

    def __init__(self, place_on_button, imagefile):

        # Image for subjects button
        self.__image = imagefile

        # Time studied
        self.__time = 0

        # Is button "on" or "off"
        self.__on = False

        # Defines which order user wants the buttons be set up
        self.__subjects_button = place_on_button

        # Endin time for studies
        self.__end_time = 0

        # Starting time for studies
        self.__start_time = 0

        # Id for the subject
        self.__id_of_the_subject = ""

        # Button for the subject is stored here
        self.__my_button = ""

        # Label for the subjects button (time)
        self.__my_label = ""


    # Get -methods: Returning the value as described in the method


    def get_label(self):

        return self.__my_label

    def get_name(self):
        return self.__id_of_the_subject

    def get_total_time(self):
        return self.__time

    def get_button(self):
        return self.__my_button

    def get_started(self):
        return self.__start_time

    def get_ended(self):
        return self.__end_time

    def get_image(self):
        return self.__image

    def get_place(self):
        return self.__subjects_button


    # Set -methods: setting the value as described in the method


    def set_label(self, label):
        self.__my_label = label

    def set_button(self, button):
        self.__my_button = button

    def set_time(self, new_time):
        self.__time = new_time

    def set_start_time(self, begun):
        self.__start_time = begun


    # Switch the button: on -> off / off -> on


    def switch(self):
        """ Switch on if off and vice versa

        :return: None
        """
        if self.__on:
            self.__on = False
        else:
            self.__on = True




    def is_on(self):
        """ Check if the button is "on"
        
        :return: True: is on
                 False: is off
        """
        return self.__on



# CLASS FOR GUI


class Ui:

    def __init__(self):

        # Create the main window and position it.
        # Also create frames and menu

        self.__root = Tk()
        self.__root.title("StudyTimer")
        self.__root.geometry("+300+10")
        self.__menu_bar = Menu(self.__root, tearoff=0)
        self.__frame4 = Frame(self.__root)
        self.__frame3 = Frame(self.__root)
        self.__frame2 = Frame(self.__root)
        self.__frame1 = Frame(self.__root, borderwidth=10)

        # Initialize main dicts and name of the file user is working on
        self.__subjects_to_be_studied = {}
        self.__previous_studies = {}
        self.__working_file = ""

        # Initialize objects, menu and create ui elements.
        if not self.init_subjects():
            return
        self.init_menu()
        self.create_elements()
        
        # Hide ui elements as we start
        self.hide_all()

        # One could argue program should show you some courses to start with,
        # but then again - in most cases user wants to continue previous
        # studies so I left it out, but it would be:
        # self.pick_your_courses()
        

    def init_subjects(self):
        """ This method reads info for the subjects to be studied from the
        file: 'config.cfg', separates the data and creates objects based on
        that data. 

        :return: True: no errors
                 False: error
        """

        try:
            cfg_file = open("config.cfg", 'r')
            inside = cfg_file.readlines()
            for line in inside:
                # read config -file line by line, remove "enter"s and split
                # data to items
                line = line.strip("\n")
                items = line.split(",")

                # Create objects (Subject)
                self.__subjects_to_be_studied[items[0]] = Subject(items[2],
                                                                  items[1])

                # Test if filedata is valid
                test = int(items[2])
                test = open(items[1])

            return True

        except Exception as error:

            messagebox.showerror("ErrorError", "Asetusten luku epäonnistui \n"
                                 + str(error))
            self.__root.destroy()
            return False


    def hide_all(self):
        """ Hide all the buttons and labels of courses.
        
        :return: None
        """

        for course in self.__subjects_to_be_studied:
            self.__subjects_to_be_studied[course].get_button().grid_forget()
            self.__subjects_to_be_studied[course].get_label().grid_forget()


    def create_elements(self):
        """ Create and set up UI elements; Buttons and labels, place frames
        
        :return: None
        """

        # Set up frames
        self.__frame1.grid(row=1, column=1)
        self.__frame2.grid(row=2, column=1)
        self.__frame3.grid(row=3, column=1)
        self.__frame4.grid(row=0, column=1)


        for subject in self.__subjects_to_be_studied:

            # Create a button for every subject to be studied
            buttonimg = PhotoImage(file=self.__subjects_to_be_studied[subject].
                                   get_image())

            # Lambda used to get id of the course as a parameter, when user is
            # pressing the button
            button = (Button(self.__frame1, image=buttonimg, command=
                      lambda b=subject: self.button_pressed(b)))

            button.img = buttonimg

            # Windows and Mac have some beef over this
            if platform.system() == "Darwin":  # if its a Mac
                button.configure(highlightthickness=3, 
                                 highlightbackground="white")
                
            else:  # if its Windows or Linux
                button.configure(bg="white", fg="white", borderwidth=7)

            # Store button to object
            self.__subjects_to_be_studied[subject].set_button(button)

            # Create and store label to object
            self.__subjects_to_be_studied[subject].\
                set_label(Label(self.__frame2, width=17))

        # Create and set the quit-button
        quit_button = Button(self.__frame3, relief="groove", text="QUIT",
                             command=self.quit_it, borderwidth=3)

        quit_button.pack(anchor="center")


        # Set buttons and labels in their places as defined
        for subject in self.__subjects_to_be_studied:

            # Get_place returns the predefined location of the button/label
            subject_column = self.__subjects_to_be_studied[subject].get_place()

            # Get_button and get_label return the button and label items
            # from the object (Subject)
            button = self.__subjects_to_be_studied[subject].get_button()
            label = self.__subjects_to_be_studied[subject].get_label()

            button.grid(row=1, column=subject_column)
            label.grid(row=1, column=subject_column)
            
            
        # Make a time stamp with a weekday to the top of the window
  
        name_of_the_day = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai",
                           "Perjantai", "Lauantai", "Sunnuntai"]
        date_time = datetime.datetime.now()
        day = getattr(date_time, "day")
        month = getattr(date_time, "month")
        year = getattr(date_time, "year")
        weekday = calendar.weekday(year, month, day)

        stamp = str(name_of_the_day[weekday]) + " " + str(day) + "."\
                                              + str(month) + "." + str(year)

        # ... and for Windows with love; some xpadding to make auto scalable
        # menu window which can fit the menu from the start too.
        datestamp = Label(self.__frame4, text=stamp, bd=5, relief="raised",
                          anchor="w", borderwidth=0,
                                 padx=100)

        datestamp.pack(anchor="e", side="left")

    
    def init_menu(self):
        """ Create the menu items
        
        :return: None
        """

        self.__root.config(menu=self.__menu_bar)

        # Filemenu
        filemenu = Menu(self.__menu_bar)
        self.__menu_bar.add_cascade(label="Tiedosto", menu=filemenu)
        filemenu.add_command(label="Lataa", command=self.load)
        filemenu.add_command(label="Tallenna", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label="Tyhjennä työpöytä", command=
                             self.empty_desktop)

        filemenu.add_separator()
        filemenu.add_command(label="Lopeta", command=self.quit_it)

        # Pick up courses -menu
        course_menu = Menu(self.__menu_bar)
        self.__menu_bar.add_cascade(label="Kurssit", menu=course_menu)
        
        course_menu.add_command(label="Valitse kurssit",
                                      command=self.pick_your_courses)

        # View studies -menu
        view_menu = Menu(self.__menu_bar)
        self.__menu_bar.add_cascade(label="Näytä opinnot", menu=view_menu)
        
        view_menu.add_command(label="Kurssin mukaan", command=
                              self.view_by_course)
        
        view_menu.add_command(label="Päivän mukaan", command=self.view_by_day)

        # Info/help -menu
        helpmenu = Menu(self.__menu_bar)
        self.__menu_bar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Ohjeet", command=self.guide)
        helpmenu.add_command(label="Tietoja", command=self.about)



    # VIEW STUDIES

    def kill_em_all(self):
        """ Closes all the open windows except the main window

        :return: None
        """

        try:
            self.__print_window.destroy()

        except:
            pass
        try:
            self.__list_window.destroy()
        except:
            pass


    def view_by_course(self):

        # Kill all view windows if open

        self.kill_em_all()

        # List courses to be chosen from. This method calls 'print_by_course'
        # This method is short on purpose, for I wanted to make own functions
        # for listing in a list_window and printing in a print_window

        self.list_courses()


    def list_courses(self):

        # Update studied for ongoing study session
        self.update_studied()
        self.__studied_courses = {}

        for course in self.__subjects_to_be_studied:
            list_of_dates = []
            
            # Find the courses that have been studied (inc. today) and add
            # to a dict;  course : list_of_days
            for day in self.__previous_studies:
                if course in self.__previous_studies[day]:
                    list_of_dates.append(day)
            if len(list_of_dates) > 0:
                self.__studied_courses[course] = list_of_dates

        # If there is no studies in memory, make a message
        if len(self.__studied_courses) == 0:
            nothing_to_see_here()
            return

        # Pop up the new window and frame
        self.__list_window = Toplevel(self.__root)
        self.__list_window.geometry("+10+10")
        check_course = Frame(self.__list_window, bd=10)
        check_course.title = "Valitse kurssi"
        check_course.pack()

        # List courses that have been studied
        for course in self.__studied_courses:
            buttonimg = PhotoImage(file=self.__subjects_to_be_studied[course].
                                   get_image())

            # Make images/buttons smaller for the list
            buttonimg = buttonimg.subsample(2)
            course_button = Button(check_course, command=lambda
                course=course: self.print_by_course(course), compound="bottom",
                                   borderwidth=7, text=course, image=buttonimg)

            course_button.img = buttonimg
            course_button.grid(row=self.__subjects_to_be_studied[course].
                               get_place(), column=1)

        # And an "OK" - button to exit.
        rdy = Button(check_course, text="Valmis", bd=3, command=
                     self.kill_em_all)

        rdy.grid(row=100, column=1, pady=7)


    def print_by_course(self, course):

        try:
            self.__print_window.destroy()

        except:
            pass

        self.update_studied()

        # Basicly the same as previous print_by_date
        self.__print_window = Toplevel(self.__root)
        self.__print_window.geometry("+120+10")
        total_frame = Frame(self.__print_window)
        total_frame.pack(side="bottom")
        total = 0

        # If data will fit nicely in the static window
        if len(self.__studied_courses[course]) < 30:

            for date in self.__studied_courses[course]:
                info = int_date2str(date) + "____________" + \
                       seconds2string(self.__previous_studies[date][course])

                total = total + int(self.__previous_studies[date][course])
                date_time_label = Label(self.__print_window, text=info)
                date_time_label.pack()

        # if not, make a scrollable window
        else:

            course_date = Scrollable(self.__print_window)
            course_date.pack()

            # Win and osx disagree on width
            if platform.system() == "Darwin":  # if its a Mac
                course_date.text.configure(width=25, height=30)

            else:  # if its Windows or Linux
                course_date.text.configure(width=14, height=30)

            # Print out courses studied on that day
            for date in self.__studied_courses[course]:
                info = int_date2str(date) + "____________" + \
                       seconds2string(self.__previous_studies[date][course])

                total = total + int(self.__previous_studies[date][course])

                date_time_label = Label(course_date, text=info)
                date_time_label.pack()
                course_date.text.window_create("end", window=date_time_label)
                course_date.text.insert("end", "\n")
            course_date.text.configure(state="disabled")

        total_label = Label(total_frame, text="Yhteensä:")
        total_studied = Label(total_frame,
                              text=seconds2string(total))
        total_studied.pack(side="right")
        total_label.pack(side="left")




    def view_by_day(self):
        """ This is a brother to a view_by_course. Both methods will first list
        course/day to choose from in a 'list_window' then accordingly print
        info for that day/course in a 'print_window'. There is a lot of same
        elements on both of these, but not enough to make function for it.
        Nevertheless, I feel repeating documentary is not necessary.

        :return: None
        """

        # Destroy previous 'View' -windows
        self.kill_em_all()
        self.list_dates()


    def list_dates(self):

        self.update_studied()

        # If there's no studydata, show message about it and return
        if len(self.__previous_studies) == 0:
            nothing_to_see_here()
            return

        # Pop a new window up and set a ready -button there for quit viewing
        self.__list_window = Toplevel(self.__root)

        # Place of the window (x,y)
        self.__list_window.geometry("+10+10")
        rdy_frame = Frame(self.__list_window)
        rdy_frame.pack(side="bottom", pady=3)
        rdy = Button(rdy_frame, text="Valmis", bd=3, command=self.kill_em_all)
        rdy.pack()

        # If all the days will fit in one window, create a static window for
        # them to be printed on
        if len(self.__previous_studies) < 30:
            check_day = Frame(self.__list_window)
            check_day.title = "Valitse päivä"
            check_day.pack()

            # Lambda used again here to deliver info to the method self.print_
            # by_date as a parameter (date)
            for dates in self.__previous_studies:
                button = Button(check_day, text=int_date2str(dates), pady=1,
                                command=lambda date=dates: self.print_by_date(
                                    date))

                button.pack(side="top")

        # If not, make a scrollable window to print 'em on
        else:
            check_day = Scrollable(self.__list_window)

            check_day.title = "Valitse päivä"
            check_day.pack()

            # There seems to be different understanding about width in a osx
            # and windows. That's why there is two different configurations
            if platform.system() == "Darwin":  # if its a Mac
                check_day.text.configure(width=10, height=30,
                                         yscrollcommand=check_day.sb.set)

            else:  # if its Windows or Linux
                check_day.text.configure(width=6, height=30,
                                         yscrollcommand=check_day.sb.set)

            # Make a button list of the days in memory as studydays, user
            # can choose from to be shown
            for dates in self.__previous_studies:
                button = Button(check_day, text=int_date2str(dates), pady=1,
                                command=lambda date=dates:
                                self.print_by_date(date))
                button.pack()
                check_day.text.window_create("end", window=button)
                check_day.text.insert("end", "\n")
            check_day.text.configure(state="disabled")


    def print_by_date(self,date):

        # Kill previous windows if there is
        try:
            self.__print_window.destroy()

        except:
            pass

        self.update_studied()
        self.__print_window = Toplevel(self.__root)
        self.__print_window.geometry("+120+10")
        self.__course_time = Frame(self.__print_window)
        self.__course_time.pack(side="right")
        total = 0
        for course in self.__previous_studies[date]:
            buttonimg = PhotoImage(file=self.__subjects_to_be_studied[course].
                                   get_image())
            buttonimg = buttonimg.subsample(2)

            course_label = Label(self.__course_time, compound="bottom",
                                 borderwidth=7, text=course,
                                 image=buttonimg)

            time_label = Label(self.__course_time,
                               text=seconds2string(
                                   self.__previous_studies[date][course]))

            total = total + int(self.__previous_studies[date][course])
            course_label.img = buttonimg
            course_label.grid(row=self.__subjects_to_be_studied[course].
                              get_place(), column=1)
            time_label.grid(row=self.__subjects_to_be_studied[course].
                            get_place(), column=2)




    # HELP MENU


    def guide(self):

        # List of strings to be printed in textbox as guide
        to_print = ["Käyttöohjeet\n",
                    "Ohjelman käynnistyessä tulee näkyviin valikko ja ikkuna,",
                    "jossa on aikaleima sekä mahdollisuus lopettaa ohjelma. ",
                    "Käyttäjän tulee valita, aloittaako hän uuden projektin",
                    "vai jatkaako edellistä. Tyhjästä aloitettaessa, valitsee",
                    "käyttäjä 'Kurssit -> valitse kurssit' -valikon takaa",
                    "avautuvasta pystyluettelosta ne kurssit, joita hän",
                    "aikoo tällä kerralla opiskella. \n ",
                    "Toinen vaihtoehto aloittaa, on ladata edellinen projekti",
                    "muistiin valikosta 'Tiedosto -> Lataa'. Tässäkin ",
                    "tapauksessa käyttäjän tulee valita, mitä aineita hän ",
                    "tässä sessiossa opiskelee. Valintaa voidaan muuttaa ",
                    "milloin vain. Opiskeltavat aineet tulevat näkyviin",
                    "vaakatasoon. \n",
                    "Mikäli projektia jatketaan samana päivänä, avautuu  ",
                    "latauksen jälkeen näkyviin tänään jo opiskellut aineet",
                    "ja niihin käytetty aika, joka jatkuu siitä, mihin ",
                    "jäätiin. Tallennuspäivämäärä määräytyy opiskelun ",
                    "lopetushetken mukaan.\n",
                    "Opiskelu ilmoitetaan alkaneeksi painamalla kurssin ",
                    "kuvaketta. Merkiksi ajastimen käynnistymisestä kuvan ",
                    "reunukset muuttuvat punaisiksi. Ajanotto pysäytetään ",
                    "painamalla kurssin kuvaa uudelleen tai aloittamalla ",
                    "toisen kurssin opiskelu, jolloin aikaisempi ajanotto ",
                    "pysähtyy. Edes Teemu Teekkari ei pysty opiskelemaan ",
                    "kahta kurssia kyllin tehokkaasti samanaikaisesti. ",
                    "Ajanoton pysähtyessä kuvan alle päivittyy ",
                    "kurssikohtaisesti sinä päivänä opiskeluun käytetty ",
                    "kokonaisaika.\n ",
                    "Opiskelun päättyessä tiedot voidaan tallentaa ja ",
                    "korvata tiedostossa uusilla tai opiskelusta voidaan ",
                    "luoda kokonaan oma tiedostonsa: 'Tiedosto -> Tallenna'.",
                    "Mikäli käyttäjä haluaa aloittaa uuden session puhtaalta ",
                    "pöydältä, tämä onnistuu Tiedosto -> Tyhjennä työpöytä ",
                    "-valikosta.\n",
                    "Kun muistissa on joko tällä kertaa opiskeltuna tai ",
                    "ladattuna vanhoja opintoja, niitä voidaan tarkastella",
                    "'Näytä opinnot' -valikosta joko päivämäärän tai kurssin",
                    "mukaan valittuna."]

        # New popup windows, new frameobject from Scrollable -class and
        # OK -button to close the infowindow
        self.__info_win = Toplevel(self.__root)
        framex = Scrollable(self.__info_win)
        framex.grid()
        ok = Button(framex, text="OK", command=self.__info_win.destroy)
        ok.pack(side="bottom")
        framex.print_guide(to_print)

    def about(self):

        # Nothing new here. Pretty much the same than previous
        to_print = ["StudyTmer β 0.1\n",
                    "Tämä ohjelma on tehty Tampereen yliopiston TIE-02101",
                    "'Ohjelmointi 1: Johdanto' kurssin viimeisenä työnä. Koodi",
                    "on kirjoitettu OSX:llä, mutta testattu myös Windows",
                    " -käyttöjärjestelmällä.\n",
                    " Ohjelma vaatii toimiakseen itse ohjelmatiedoston",
                    " lisäksi config.cfg -tiedoston, jossa on määritelty",
                    " kurssien ominaisuudet sekä tässä tässä tiedostossa ",
                    "nimetyt kuvatiedostot (150x100) \n",
                    "© Rauli Virtanen 2019"]

        self.__info_win = Toplevel(self.__root)
        framex = Scrollable(self.__info_win)
        framex.grid()
        ok = Button(framex, text="OK", command=self.__info_win.destroy)
        ok.pack(side="bottom")

        # This method, 'print about' takes another parameter for a recursive
        # loop for a first index of a line so 'print about' will print data
        # line by line some delay between lines.
        framex.print_about(0, to_print)



    # PICK UP COURSES

    def change_courses(self):
        """ Important dictionary here is 'subjects to be studied'. This will
        show or hide buttons as picked in 'pick your courses' method

        :return: None
        """

        for course in self.__subjects_to_be_studied:

            # 0 means subject was unchecked when information was sent. 1 means
            # subject was checked. Record is kept for every course.

            # Make changes accordingly, show or forget
            if self.__chosen_ones[course].get() == 0:
                self.__subjects_to_be_studied[course].get_button().\
                    grid_forget()
                self.__subjects_to_be_studied[course].get_label().grid_forget()

            if self.__chosen_ones[course].get() == 1:
                self.__subjects_to_be_studied[course].get_button().\
                    grid(row=1, column=self.__subjects_to_be_studied[course].
                         get_place())

                self.__subjects_to_be_studied[course].get_label().\
                    grid(row=2, column=self.__subjects_to_be_studied[course].
                         get_place())

                self.__subjects_to_be_studied[course].get_label().configure(
                    text="--:--")
                self.kill_em_all()



    def pick_your_courses(self):
        """ Create checkbutton widget for courses

        :return: None
        """

        # Make windows, frame, reset data and  'OK' and 'Cancel' buttons
        # and pack widgets

        self.kill_em_all()
        self.update_studied()
        self.__list_window = Toplevel()
        self.__list_window.title("Valitse kurssit")
        self.__list_window.geometry("+5+10")
        frame = Frame(self.__list_window, bd=15)
        frame.pack(side="bottom")

        self.__chosen_ones = {}
        ok = Button(frame, text="Ok", width=7, height=2,
                    command=self.change_courses)

        cancel = Button(frame, text="Cancel", width=7, height=2,
                        command=self.kill_em_all)

        ok.pack(side="left", ipadx=3)
        cancel.pack(side="right")


        # Make checkbox+label for every course available
        for course in self.__subjects_to_be_studied:

            # Set variable in a dict of 'chosen ones' to store if button
            # is checked
            self.__chosen_ones[course] = IntVar()
            buttonimg = PhotoImage(file=self.__subjects_to_be_studied[course].
                                   get_image())
            buttonimg = buttonimg.subsample(2)

            # Save variable (1/0) as value to the dict, key course id
            c_button = Checkbutton(self.__list_window,compound="bottom",
                                   text=course, image=buttonimg,variable=
                                   self.__chosen_ones[course])
            c_button.img = buttonimg
            c_button.pack(side="top")


    def clear_it_all(self):
        """ This is harsh. Killing, deleting, destroying everything and then
        building the frames again, initializing subjects and creating ui
        elements and hiding them - as we did at the beginning. Ie. resetting
        all.
        :return: None
        """

        self.kill_em_all()
        self.__previous_studies = {}
        self.__frame1.destroy()
        self.__frame2.destroy()
        self.__frame3.destroy()
        self.__frame4.destroy()

        self.__frame4 = Frame(self.__root)
        self.__frame3 = Frame(self.__root)
        self.__frame2 = Frame(self.__root)
        self.__frame1 = Frame(self.__root, borderwidth=10)

        self.init_subjects()
        self.create_elements()
        self.hide_all()


    # FILEMENU

    def load(self):

        we_shall_continue = False

        # If there is unsaved data
        if len(self.__previous_studies) > 0:

            # Ask if user wants to continue, since this clears old studies
            # from the memory
            we_shall_continue = ask_for_it()

        # If user wants to continue or there is nothing to loose (previous
        # studies dict is empty):
        if we_shall_continue or len(self.__previous_studies) == 0:

            try:
                # Only .stf files are given to be loaded
                file_type = [('Study Timer File', '*.stf')]
                file_name = filedialog.askopenfilename(filetypes=file_type)
                file = open(file_name, 'r')

                # Parse filename with directory to bare filename
                path = file_name.split("/")
                name = path[len(path)-1]

                # Read what's inside file
                inside = file.readlines()

                # and reset everything
                self.clear_it_all()

                # For every line (one line for each day)...
                for line in inside:

                    # get the info using functions 'get_date' and 'get_courses'
                    line = line.strip("\n")
                    day = get_date(line)
                    courses = get_courses(line)

                    # ...and store data in 'previous_studies' dict
                    self.__previous_studies[day] = courses

                    # If there's data for studies for today from file...
                    if day == today():

                        # ...hide all buttons and labels...
                        self.hide_all()

                        #...and show courses which were studied already today
                        for course in self.__previous_studies[day]:
                            course_obj = self.__subjects_to_be_studied[course]
                            course_obj.set_time(int(courses[course]))
                            course_obj.get_button().grid(row=1, column=
                                                         course_obj.
                                                         get_place())

                            course_obj.get_label().grid(row=2, column=
                                                        course_obj.get_place())

                # Change working title and update studies = show time
                self.__working_file = name
                title = "StudyTimer - " + name
                self.__root.title(title)
                self.update_studied()

            # Canceling operation to load seems to be handeled as IOError,
            # but we don't want so show any errormessages for that
            except IOError:
                pass

            # On the other hand if anything goes wrong while reading the file
            # there will be an error message.
            except:

                messagebox.showerror("ErrorError", "Tiedosto on särki")



    def save(self):

        rows = []
        # Save today studied to dict previous_studies = update studies
        self.update_studied()

        # For every day studied in memory...
        for day in self.__previous_studies:
            courses = ""

            # ... take studied courses, course by course....
            for course in self.__previous_studies[day]:

                # ... and bulid the ending of a line to be written in file
                # in form of 'course1:time1, course2:time2....'.
                course_time = course + ":" + str(self.__previous_studies
                                                 [day][course])

                courses = courses + course_time + ","
            # Then add day and ';' in the beginning of the line...
            row = str(day) + ";" + courses

            # ...and remove last extra ','...
            row = row[0:len(row)-1]

            # and finally append row in the list of rows
            rows.append(row)


        # Use tkinter method to ask for a name of the file working title
        # as default
        file = filedialog.asksaveasfile(mode='w', defaultextension=".stf",
                                        initialfile = self.__working_file)

        # If nothing was chosen, get back
        if file is None:
            return

        # Write rows to file
        for row in rows:
            file.writelines(row+"\n")
        file.close()

        # Inform about saving the file and change title

        # Separate the filename
        path = str(file)
        path = path.split("/")
        name = path[len(path) - 1].split(".stf")

        # Change title
        title = name[0] + ".stf"
        self.__root.title("StudyTimer - " + title)
        self.__working_file = title

        # Show message with the filename
        messagebox.showinfo("Tallennus valmis",
                            'Tiedostosi "{:s}" on nyt tallennettu '
                            'onnistuneesti.'.format(title))


    def empty_desktop(self):
        """ Resets the desktop after confirmation and sets working title
        just 'StudyTimer'.

        :return: None
        """

        if ask_for_it():
            self.clear_it_all()
            self.__root.title("StudyTimer")
            self.__working_file = ""


    def update_studied(self):
        """ Updates previouslu studied with recent today studies and views
        time under course icon.

        :return: None
        """

        self.switch_all_off()

        # Local dictionary to store studytimes in form of course id : time
        opittu = {}

        # If there has been studying today...
        if today() in self.__previous_studies:
            # ...reset todays info to avoid duplicates
            self.__previous_studies[today()] = {}

        # For every course chosen to be viewed...
        for course in self.__subjects_to_be_studied:

            # ...check if it has been studied...
            if self.__subjects_to_be_studied[course].get_total_time() != 0:
                # and if so, update 'previous studies'...
                opittu[course] = self.__subjects_to_be_studied[course].\
                                      get_total_time()
                self.__previous_studies[today()] = opittu
                # and make time visible in objects label in form of:
                # hh:mm:ss
                show_time = seconds2string(opittu[course])
                self.__subjects_to_be_studied[course].get_label().\
                    configure(text=show_time)




    def start(self):

        self.__root.mainloop()


    def quit_it(self):
        """ After asking for a confirmation, kill the main window.

        :return: None
        """

        if ask_for_it():
            self.__root.destroy()
        else:
            return


    def switch_off(self, button):
        """ Switch off the button given

        :param button: button/course which will be switched off
        :return: None
        """

        # Making code easier to read setting up 'course' as object in question
        course = self.__subjects_to_be_studied[button]

        # Turn button border white. Windows and Mac have different reactions
        # for same commands, hence...
        if platform.system() == "Darwin":  # If it's a Mac
            course.get_button().configure(highlightthickness=3,
                                          highlightbackground="white")
        else:  # If its Windows or Linux
            course.get_button().configure(bg="white", fg="white")

        # time.time returns epoch time which is useful for this purpose
        # counting duration of the studies. If date changes during studies,
        # that wont mess counting of duration up.
        end_time = time.time()
        duration = end_time - course.get_started()
        total_time = int(course.get_total_time()) + int(duration)
        
        # Add duration of study in this session to duration of the studies
        # previously today and print it.
        course.set_time(total_time)
        course.get_label().configure(text=seconds2string(total_time))


    def switch_all_off(self):
        
        # If the course is chosen to be studied at the time...
        for course in self.__subjects_to_be_studied:
            # ...and if it is on...
            if self.__subjects_to_be_studied[course].is_on():
                
                # ...switch it off...
                self.switch_off(course)
                
                # ...and change it's on/off status. 
                self.__subjects_to_be_studied[course].switch()


    def switch_on(self, button):
        
        # Pretty much the same as 'switch off' but other way around.

        # Switch button border red
        course = self.__subjects_to_be_studied[button]
        if platform.system() == "Darwin":  # if its a Mac
            course.get_button().configure(highlightthickness=3,
                                          highlightbackground="red")
        else:  # if its Windows or Linux
            course.get_button().configure(bg="red", fg="red")

        # and start the clock
        course.set_start_time(time.time())


    def button_pressed(self, button):

        if self.__subjects_to_be_studied[button].is_on():
            self.switch_off(button)
            self.__subjects_to_be_studied[button].switch()
        else:
            self.switch_on(button)
            self.__subjects_to_be_studied[button].switch()
            for aine in self.__subjects_to_be_studied:
                if self.__subjects_to_be_studied[aine].is_on() and aine != button:
                    self.switch_off(aine)
                    self.__subjects_to_be_studied[aine].switch()


# Static and helper functions

def ask_for_it():
    if messagebox.askyesno("Oletko varma?", "Tallentamattomat opiskelut "
                                            "menetetään.\n(Tietokoneen "
                                            "muistista, ei sinun)"):

        return True
    else:
        return False


def nothing_to_see_here():
    messagebox.showerror("Tyhjä arpa", " Ensin pitää opiskella,\n "
                                       "sitten vasta ihailla tuloksia \n")


def today():
    """ Gets today and changes it in stf -file standard form 
    
    :return: stamp (string) of today in form of ddmmyyyy
    """

    date_time = datetime.datetime.now()
    day = str(getattr(date_time, "day"))
    month = str(getattr(date_time, "month"))
    year = str(getattr(date_time, "year"))

    # Windows seems to get datetime.now in single digits when possible. Extra 
    # zeroes need to be added.
    if len(day) < 2:
        day = "0" + day

    if len(month) < 2:
        month = "0" + month

    stamp = day + month + str(year)

    return stamp


def int_date2str(date):
    """ Changes integer given time to a string to be printed
    
    :param date: Date needed to be edited
    :return: string of time with dots
    """

    day = str(date[0:2])
    month = str(date[2:4])
    year = str(date[4:8])
    time_str_dots = day + "." + month + "." + year

    return time_str_dots


def seconds2string(seconds):
    """ Transforms given seconds to string of hours, minutes and seconds
    
    :param seconds: Numer of the seconds wanted to be transformed
    :return: string of time in form of hh:mm:ss
    """
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    string = '{:d}:{:02d}:{:02d}'.format(h, m, s)

    return string


def get_courses(row):
    """ Gets studied courses out of line of file or previous studies
    
    :param row: Line to be inspected
    :return: Dictionary of courses in form of course id : studied time
    """
    courses = {}
    
    # Parsing the line in form of ddmmyyyy;course1:time1,course2:time2...
    strip_day = row.split(";")
    course_time = strip_day[1].split(",")
    for item in course_time:
        c_t = item.split(":")
        courses[c_t[0]] = c_t[1]

    return courses


def get_date(row):
    """ Finds the date from a given line
    
    :param row: Line to be inspected for date
    :return: Date from the line
    """

    day = row.split(";")
    return day[0]


def main():

    # Just creating the Ui -object and starting it.

    here_we_go = Ui()
    here_we_go.start()

main()
