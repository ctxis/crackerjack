class TemplateManager:
    def get_hashcat_running_text(self, state):
        state = int(state)
        text = 'Unknown'

        if state == 0:
            text = 'Not Started'
        elif state == 1:
            text = 'Running'
        elif state == 2:
            text = 'Stopped'
        elif state == 3:
            text = 'Finished'
        elif state == 4:
            text = 'Paused'
        elif state == 5:
            text = 'Cracked'
        elif state == 98:
            text = 'Error'

        return text

    def get_hashcat_running_class(self, state):
        state = int(state)
        text = ''

        if state == 0:
            text = 'info'
        elif state == 1:
            text = 'success'
        elif state == 2:
            text = 'danger'
        elif state == 3:
            text = 'info'
        elif state == 4:
            text = 'warning'
        elif state == 5:
            text = 'success'
        elif state == 98:
            text = 'danger'

        return text
