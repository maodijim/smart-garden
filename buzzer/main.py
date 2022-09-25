from machine import Pin, PWM, ADC, deepsleep
import time
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("beeper")
tones = {
    ' ': 0,
    'NOTE_E5': 659,
    'NOTE_D5': 587,
    'NOTE_FS4': 370,
    'NOTE_GS4': 415,
    'NOTE_CS5': 554,
    'NOTE_B4': 494,
    'NOTE_D4': 294,
    'NOTE_E4': 330,
    'NOTE_A4': 440,
    'NOTE_CS4': 277,
}


def play_nokia(tempo=5):
    beeper = PWM(Pin(14, Pin.OUT), freq=440, duty=512)
    melody = [
        'NOTE_E5', 'NOTE_D5', 'NOTE_FS4', 'NOTE_GS4', 'NOTE_CS5',
        'NOTE_B4', 'NOTE_D4', 'NOTE_E4', 'NOTE_B4', 'NOTE_A4',
        'NOTE_CS4', 'NOTE_E4', 'NOTE_A4']
    rhythm = [
        16, 16, 8, 8, 16,
        16, 8, 8, 16, 16,
        8, 8, 4]

    for tone, length in zip(melody, rhythm):
        beeper.freq(tones[tone])
        log.info('tone: {}, length: {}'.format(tones[tone], length))
        time.sleep(tempo/length)
    beeper.deinit()


def read_soil_sensor(pin_num):
    adc = ADC(Pin(pin_num))
    adc.atten(ADC.ATTN_11DB)
    return adc.read()


if __name__ == '__main__':
    while True:
        soil_reading = read_soil_sensor(32)
        log.info('soil sensor value: {}'.format(soil_reading))
        if soil_reading < 2000:
            # faster the tempo when the soil is wet
            tempo = 5 * (soil_reading - 1000) / 1000
            play_nokia(tempo=tempo)
            time.sleep(2)
            play_nokia(tempo=tempo)
        deepsleep(120*1000)
