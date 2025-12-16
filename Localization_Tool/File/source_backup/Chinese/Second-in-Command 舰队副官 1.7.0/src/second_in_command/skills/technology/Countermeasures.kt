package second_in_command.skills.technology

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.skills.ElectronicWarfareScript
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Countermeasures : SCBaseSkillPlugin() {

    var PER_SHIP_BONUS = 1f

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("-10%% 被探测范围", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("舰队中每艘部署的舰船都可提供 ${PER_SHIP_BONUS.toInt()}%% 的 电子战强度*", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("所有舰船的自动射击精度略有提高", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addSpacer(10f)

        var max = ElectronicWarfareScript.BASE_MAXIMUM.toInt()

        tooltip.addPara("*敌人武器射程会根据你部署舰船的 电子战强度 " +
	"被降低至多 $max%%}。该减益会根据 敌方电子战强度 " +
                "对 己方电子战强度 的比例减弱。" + "对战机无效，影响包括导弹在内的所有武器。", 0f, Misc.getGrayColor(), Misc.getHighlightColor(),
            "$max%")
    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        stats!!.dynamic.getMod(Stats.ELECTRONIC_WARFARE_FLAT).modifyFlat(id, PER_SHIP_BONUS)
        stats.autofireAimAccuracy.modifyFlat(id, 0.2f)

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData?, amunt: Float?) {
        data!!.fleet.stats.detectedRangeMod.modifyMult("sc_countermeasures", 0.9f, "Countermeasures")
    }

    override fun onDeactivation(data: SCData?) {
        data!!.fleet.stats.detectedRangeMod.unmodify("sc_countermeasures")
    }

}