package com.example.hiwin.teacher_version_bob.fragment;

import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import android.widget.ImageView;
import com.example.hiwin.teacher_version_bob.R;
import com.example.hiwin.teacher_version_bob.data.ObjectSpeaker;
import com.example.hiwin.teacher_version_bob.data.framework.object.DataObject;
import pl.droidsonroids.gif.GifDrawable;

import java.io.IOException;

public class FaceFragment extends Fragment {

    private DataObject object;
    private boolean speak;
    private boolean endByAnimation;

    public enum FaceType {
        car(R.raw.face_cry), cake(R.raw.face_happy), knife(R.raw.face_happy),
        bowl(R.raw.face_happy), person(R.raw.face_happy), bird(R.raw.face_happy),
        cat(R.raw.face_happy), bottle(R.raw.face_happy);
        private final int id;

        FaceType(int id) {
            this.id = id;
        }

        public int getId() {
            return id;
        }
    }

    private GifDrawable drawable;
    private ObjectSpeaker speaker;
    private FragmentListener listener;
    private ImageView imageView;


    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View root = inflater.inflate(R.layout.fragment_face, container, false);
        speaker = new ObjectSpeaker(getContext());
        imageView = (ImageView) root.findViewById(R.id.face_gif);
        return root;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        start();
    }

    public void warp(Context context, DataObject object, boolean speak, boolean endByAnimation) throws IOException {
        this.object = object;
        this.speak = speak;
        this.endByAnimation=endByAnimation;
        drawable = new GifDrawable(context.getResources(), FaceType.valueOf(object.getName()).getId());
        drawable.setLoopCount(5);
        drawable.stop();

        Log.d("DDDDDD","warp:"+hashCode()+":"+drawable.hashCode());
        if (endByAnimation) {
            drawable.addAnimationListener(i -> {
                Log.d("DDDDDD",drawable.hashCode()+":end:"+i);
                if (listener != null && i + 1 == drawable.getLoopCount()) {
                    listener.end();
                }

            });
        }
    }

    private void start() {
        imageView.setImageDrawable(drawable);
        drawable.start();
        if (speak &&!endByAnimation) {
            speaker.setSpeakerListener(() -> {
                if (listener != null)
                    listener.end();
            });
            speaker.speakFully(object);
        }

        if (listener != null)
            listener.start();
    }

    public void setListener(FragmentListener listener) {
        this.listener = listener;
    }

}