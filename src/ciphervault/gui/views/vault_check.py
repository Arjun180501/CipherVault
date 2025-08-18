from ciphervault.gui.views.login_window import LoginWindow
from ciphervault.gui.views.init_window import InitWindow
from ciphervault.gui.views.popup_dialog import PopupDialog
from ciphervault.gui.utils.utils import load_vaults

class vault_check():
    @staticmethod
    def check_vault_exists(parent_window=None):
        vaults = load_vaults()
        if not vaults:
            dialog = PopupDialog(
                title="No Vaults Found",
                message="No vaults found. Create one?",
                yes_label="Yes",
                no_label="No",
            )
            result = dialog.exec()

            if result == PopupDialog.DialogCode.Accepted:
                return 0
            else:
                return 1
        else:
            return 2
