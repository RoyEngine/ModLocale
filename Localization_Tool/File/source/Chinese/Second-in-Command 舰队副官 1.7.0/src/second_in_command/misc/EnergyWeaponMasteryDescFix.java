package second_in_command.misc;

import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.impl.campaign.skills.EnergyWeaponMastery;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

public class EnergyWeaponMasteryDescFix  extends EnergyWeaponMastery.Level1 {

    @Override
    public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, TooltipMakerAPI info, float width) {

        init(stats, skill);

        tc = Misc.getTextColor();
        hc = Misc.getHighlightColor();



        info.addPara("近距离作战时最高提升 %s 的能量武器伤害，其加成也取决于发射舰船当前的幅能水平",
                0f, hc, hc,
                "+" + (int) EnergyWeaponMastery.ENERGY_DAMAGE_PERCENT + "%"
        );


        info.addPara(indent + "距离 %s 或更近时加成最高，" +
                        "距离 %s 或更远时将无加成",
                0f, tc, hc,
                "" + (int) EnergyWeaponMastery.MIN_RANGE,
                "" + (int) EnergyWeaponMastery.MAX_RANGE
        );
    }
}
