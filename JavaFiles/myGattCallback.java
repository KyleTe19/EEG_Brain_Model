package org.montage.ble;

import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothProfile;
import android.util.Log;

public class MyGattCallback extends BluetoothGattCallback {
    @Override
    public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
        if (newState == BluetoothProfile.STATE_CONNECTED) {
            Log.d("MyGattCallback", "Connected to GATT server.");
            gatt.discoverServices();
        } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
            Log.d("MyGattCallback", "Disconnected from GATT server.");
        }
    }

    @Override
    public void onServicesDiscovered(BluetoothGatt gatt, int status) {
        Log.d("MyGattCallback", "Services discovered with status: " + status);
    }
}