package in.vkvnalbari.vkvtt;

import android.app.Activity;
import android.net.Uri;
import android.os.Bundle;

import androidx.browser.customtabs.CustomTabsIntent;

public class MainActivity extends Activity {
    private static final String HOME = "https://ritwik17c.github.io/vkvtt/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        CustomTabsIntent customTabsIntent = new CustomTabsIntent.Builder()
                .setShowTitle(true)
                .build();
        customTabsIntent.launchUrl(this, Uri.parse(HOME));
        finish();
    }
}
