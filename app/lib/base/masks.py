class MasksManager:
    def __init__(self, filesystem, masks_path):
        self.filesystem = filesystem
        self.masks_path = masks_path

    def get_masks(self):
        return self.filesystem.get_files(self.masks_path)

    def is_valid_mask(self, mask):
        masks = self.get_masks()
        return mask in masks

    def get_mask_path(self, mask):
        if not self.is_valid_mask(mask):
            return ''

        masks = self.get_masks()
        mask = masks[mask]
        return mask['path']
