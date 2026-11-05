package com.vithel.arseniygod;

import android.content.ComponentName;
import android.content.pm.PackageManager;
import android.os.Build;
import org.apache.cordova.CallbackContext;
import org.apache.cordova.CordovaPlugin;
import org.json.JSONArray;
import org.json.JSONException;
import java.util.ArrayList;
import java.util.List;

public class IconSwitcher extends CordovaPlugin {
    private static final String[] ICONS = {"default", "dark", "green", "blue", "pink"};
    private ComponentName component(String icon) {
        return new ComponentName(cordova.getActivity(), cordova.getActivity().getPackageName() + ".Icon_" + icon);
    }
    @Override public boolean execute(String action, JSONArray args, CallbackContext callback) throws JSONException {
        if (!"select".equals(action)) return false;
        String selected = args.getString(0);
        boolean valid = false;
        for (String icon : ICONS) if (icon.equals(selected)) valid = true;
        if (!valid) { callback.error("Неизвестная иконка"); return true; }
        try {
            PackageManager pm = cordova.getActivity().getPackageManager();
            if (Build.VERSION.SDK_INT >= 33) {
                List<PackageManager.ComponentEnabledSetting> changes = new ArrayList<>();
                for (String icon : ICONS) changes.add(new PackageManager.ComponentEnabledSetting(component(icon), icon.equals(selected) ? PackageManager.COMPONENT_ENABLED_STATE_ENABLED : PackageManager.COMPONENT_ENABLED_STATE_DISABLED, PackageManager.DONT_KILL_APP));
                pm.setComponentEnabledSettings(changes);
            } else {
                pm.setComponentEnabledSetting(component(selected), PackageManager.COMPONENT_ENABLED_STATE_ENABLED, PackageManager.DONT_KILL_APP);
                for (String icon : ICONS) if (!icon.equals(selected)) pm.setComponentEnabledSetting(component(icon), PackageManager.COMPONENT_ENABLED_STATE_DISABLED, PackageManager.DONT_KILL_APP);
            }
            callback.success();
        } catch (Exception e) { callback.error("Не удалось сменить иконку: " + e.getClass().getSimpleName()); }
        return true;
    }
}
