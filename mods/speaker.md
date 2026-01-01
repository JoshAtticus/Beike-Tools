## 2. "Speaker" Deshittifier
The speaker is a piezo buzzer (aka not a speaker). To prevent pain and suffering:

- Edit squashfs-root/etc/audio_policy.conf
- Reduce spk_gain max value from 60 to 40

Alternatively, open the camera and desolder it from the board, problem solved