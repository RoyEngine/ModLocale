package second_in_command.misc

import com.fs.starfarer.api.characters.MutableCharacterStatsAPI
import com.fs.starfarer.api.characters.SkillSpecAPI
import com.fs.starfarer.api.impl.campaign.skills.CombatEndurance
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc

class CombatEnduranceDescFix : CombatEndurance.Level4() {

    override fun createCustomDescription(stats: MutableCharacterStatsAPI?,  skill: SkillSpecAPI?, info: TooltipMakerAPI?, width: Float) {

        initElite(stats, skill)

        tc = Misc.getTextColor()
        hc = Misc.getHighlightColor()

        info!!.addPara("当船体结构值低于 %s 时，每秒维修 %s 结构值；最大总维修量为" + " %s 点结构值或 %s 的总结构值，取较大值", 0f, hc, hc,
            "" + Math.round(CombatEndurance.MAX_REGEN_LEVEL * 100f) + "%",  //"" + (int)Math.round(REGEN_RATE * 100f) + "%",
            "" + Misc.getRoundedValueMaxOneAfterDecimal(CombatEndurance.REGEN_RATE * 100f) + "%",
            "" + Math.round(CombatEndurance.TOTAL_REGEN_MAX_POINTS) + "",
            "" + Math.round(CombatEndurance.TOTAL_REGEN_MAX_HULL_FRACTION * 100f) + "%")
    }

}