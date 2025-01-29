package no11;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;

public class Home extends JFrame implements ActionListener {
    private RoundButton btnShokyuu, btnChuukyuu, btnJoukyuu, btnRules;

    public Home() {
        setTitle("レベル選択");
        setSize(400, 400);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();

        
        JLabel instructionLabel = new JLabel("難度を選んでね");
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.insets = new Insets(20, 20, 10, 20); 
        gbc.anchor = GridBagConstraints.CENTER;
        add(instructionLabel, gbc);

  
        gbc.gridy = 1;
        JLabel titleLabel = new JLabel("レベル選択");
        add(titleLabel, gbc);

        // ボタンの作成
        btnShokyuu = new RoundButton("初級");
        btnChuukyuu = new RoundButton("中級");
        btnJoukyuu = new RoundButton("上級");
        btnRules = new RoundButton("ルール");

  
        JPanel panel = new JPanel();
        panel.setLayout(new GridLayout(1, 3, 10, 10)); 
        panel.add(btnShokyuu);
        panel.add(btnChuukyuu);
        panel.add(btnJoukyuu);

        gbc.gridy = 2;
        gbc.insets = new Insets(20, 20, 10, 20); 
        add(panel, gbc);

 
        gbc.gridy = 3;
        gbc.insets = new Insets(10, 20, 20, 20); 
        add(btnRules, gbc);


        btnShokyuu.addActionListener(this);
        btnChuukyuu.addActionListener(this);
        btnJoukyuu.addActionListener(this);
        btnRules.addActionListener(this);

        
        setLocationRelativeTo(null);
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == btnShokyuu) {
            dispose(); 
            shokyuu shokyuuLevel = new shokyuu();
            shokyuuLevel.setVisible(true);
        } else if (e.getSource() == btnChuukyuu) {
            dispose(); 
            chuukyuu chuukyuuLevel = new chuukyuu();
            chuukyuuLevel.setVisible(true);
        } else if (e.getSource() == btnJoukyuu) {
            dispose(); 
            joukyuu joukyuuLevel = new joukyuu();
            joukyuuLevel.setVisible(true);
        } else if (e.getSource() == btnRules) {
            JOptionPane.showMessageDialog(this, "大きい順と小さい順を判別して" +
                "ボタンを押してポイントを稼ごう。\n" +
                "中級からはボタンの数が増えて\n" +
                "上級は押しても色が出なくなる。");
        }
    }

    public static void main(String[] args) {
        Home frame = new Home();
        frame.setVisible(true);
    }
}
